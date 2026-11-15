"""Preserve a qualified firmware transport while updating its DarwinBoot module."""
import hashlib
import lzma
import os
import struct
import tempfile
import uuid
import zlib
from pathlib import Path

from .util import Error, log, run, sha256_file, tool

LZMA_GUID = uuid.UUID('ee4e5898-3914-4259-9d6e-dc7bd79403cf').bytes_le
MAX_FV = 64 << 20


def align(value, boundary):
    return (value + boundary - 1) & -boundary


def size24(data, offset):
    if offset < 0 or offset + 3 > len(data):
        raise Error('truncated firmware size')
    return int.from_bytes(data[offset:offset + 3], 'little')


def put24(data, offset, value):
    if not 4 <= value < 0xffffff:
        raise Error('firmware section exceeds the supported size')
    data[offset:offset + 3] = value.to_bytes(3, 'little')


def sections(data, start, end):
    while start < end:
        length = size24(data, start)
        if length < 4 or start + length > end:
            raise Error('invalid firmware section boundary')
        yield start, data[start + 3], bytes(data[start:start + length])
        start = align(start + length, 4)
    if start != align(end, 4):
        raise Error('invalid firmware section alignment')


def fv_files(data, offset=0):
    if offset + 72 > len(data) or data[offset + 40:offset + 44] != b'_FVH':
        raise Error('firmware volume header missing')
    length = struct.unpack_from('<Q', data, offset + 32)[0]
    header = struct.unpack_from('<H', data, offset + 48)[0]
    if length > MAX_FV or header < 72 or header & 1 or header > length or offset + length > len(data):
        raise Error('invalid firmware volume size')
    if sum(struct.unpack_from(f'<{header // 2}H', data, offset)) & 65535:
        raise Error('firmware volume header checksum mismatch')
    at, end, files = offset + header, offset + length, []
    while at + 24 <= end and data[at:at + 24] != b'\xff' * 24:
        size = size24(data, at + 20)
        if size < 24 or size == 0xffffff or at + size > end:
            raise Error('invalid firmware file boundary')
        file = bytes(data[at:at + size])
        if file[19] not in (0, 4):
            raise Error('unsupported firmware file alignment or checksum attributes')
        check = bytearray(file[:24])
        check[17] = check[23] = 0
        if sum(check) & 255:
            raise Error('firmware file header checksum mismatch')
        files.append((at, str(uuid.UUID(bytes_le=file[:16])), file))
        at = align(at + size, 8)
    if any(value != 255 for value in data[at:end]):
        raise Error('unexpected data after firmware files')
    return header, length, files


def compressed_volume(firmware):
    _, _, root = fv_files(firmware)
    found = []
    for file_at, _, file in root:
        if file[18] != 0x0b:
            continue
        for section_at, kind, section in sections(file, 24, len(file)):
            if kind != 2 or len(section) < 24 or section[4:20] != LZMA_GUID:
                continue
            data_at = struct.unpack_from('<H', section, 20)[0]
            if data_at != 24:
                raise Error('unsupported compressed firmware section header')
            try:
                decoder = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE, memlimit=MAX_FV * 2)
                expanded = decoder.decompress(section[data_at:], max_length=MAX_FV + 1)
            except lzma.LZMAError as error:
                raise Error(f'invalid compressed firmware volume: {error}') from error
            if len(expanded) > MAX_FV or not decoder.eof or decoder.unused_data:
                raise Error('compressed firmware volume exceeds bounds or has trailing data')
            volumes = [(at, content) for at, kind, content in sections(expanded, 0, len(expanded)) if kind == 0x17]
            if len(volumes) != 1 or volumes[0][0] != 4 or expanded[:4] != b'\x04\0\0\x19':
                raise Error('unsupported nested firmware volume layout')
            fv_files(expanded, 8)
            found.append((file_at, file, section_at, section, expanded))
    if len(found) != 1:
        raise Error('expected one LZMA firmware volume')
    return found[0]


def loader_pe(firmware, identifier):
    expanded = compressed_volume(firmware)[4]
    matches = [file for _, guid, file in fv_files(expanded, 8)[2] if guid == identifier]
    if len(matches) != 1:
        raise Error('expected exactly one selected firmware loader')
    images = [section[4:] for _, kind, section in sections(matches[0], 24, len(matches[0])) if kind == 0x10]
    if len(images) != 1 or images[0][:2] != b'MZ':
        raise Error('selected firmware loader has no PE image')
    return images[0]


def file_checksum(file):
    file[16] = 0
    header = bytearray(file[:24])
    header[17] = header[23] = 0
    file[16] = (-sum(header)) & 255


def replace_loader(firmware, pe, identifier):
    """Keep unrelated files byte-identical and refuse unsupported FV attributes."""
    if pe[:2] != b'MZ':
        raise Error('replacement loader is not a PE image')
    file_at, outer, section_at, section, expanded = compressed_volume(firmware)
    header, _, original = fv_files(expanded, 8)
    if section_at != 24 or len(section) + 24 != len(outer):
        raise Error('compressed firmware file contains additional sections')
    rebuilt = bytearray(expanded[:8 + header])
    count = 0
    for _, guid, file in original:
        rebuilt.extend(b'\xff' * (align(len(rebuilt), 8) - len(rebuilt)))
        if guid == identifier:
            item = bytearray(file[:24])
            for at, kind, content in sections(file, 24, len(file)):
                next_at = align(at + len(content), 4)
                if kind == 0x10:
                    content = bytearray(b'\0\0\0\x10' + pe)
                    put24(content, 0, len(content))
                    count += 1
                item.extend(content)
                if next_at < len(file):
                    item.extend(b'\0' * (align(len(item), 4) - len(item)))
            put24(item, 20, len(item))
            file_checksum(item)
            file = bytes(item)
        rebuilt.extend(file)
    if count != 1:
        raise Error('expected exactly one loader PE replacement')
    # The qualified template uses one uniform 4 KiB block map.
    blocks, block_size, terminator = struct.unpack_from('<IIQ', expanded, 64)
    if block_size != 4096 or terminator or blocks * block_size != len(expanded) - 8:
        raise Error('unsupported nested firmware block map')
    length = align(len(rebuilt) - 8, block_size)
    if length > MAX_FV:
        raise Error('rebuilt firmware volume exceeds bounds')
    rebuilt.extend(b'\xff' * (8 + length - len(rebuilt)))
    struct.pack_into('<Q', rebuilt, 40, length)
    struct.pack_into('<I', rebuilt, 64, length // block_size)
    put24(rebuilt, 4, length + 4)
    struct.pack_into('<H', rebuilt, 58, 0)
    struct.pack_into('<H', rebuilt, 58, (-sum(struct.unpack_from(f'<{header // 2}H', rebuilt, 8))) & 65535)
    changed = fv_files(rebuilt, 8)[2]
    if len(changed) != len(original):
        raise Error('firmware module count changed')
    for before, after in zip(original, changed):
        if before[1] != after[1] or (before[1] != identifier and before[2] != after[2]):
            raise Error('an unrelated firmware module changed')
    packed = bytearray(lzma.compress(bytes(rebuilt), format=lzma.FORMAT_ALONE,
                                    filters=[{'id': lzma.FILTER_LZMA1, 'dict_size': 1 << 24, 'lc': 3, 'lp': 0, 'pb': 2}]))
    packed[5:13] = len(rebuilt).to_bytes(8, 'little')
    updated = bytearray(section[:24]) + packed
    put24(updated, 0, len(updated))
    file = bytearray(outer[:24]) + updated
    put24(file, 20, len(file))
    file_checksum(file)
    _, _, root = fv_files(firmware)
    if root[-1][0] != file_at or file_at + len(file) > len(firmware):
        raise Error('replacement firmware cannot fit without moving root modules')
    result = firmware[:file_at] + file + b'\xff' * (len(firmware) - file_at - len(file))
    if loader_pe(result, identifier) != pe:
        raise Error('replacement loader failed firmware round-trip verification')
    return result, {'loader_guid': identifier, 'loader_sha256': hashlib.sha256(pe).hexdigest(),
                    'loader_bytes': len(pe), 'preserved_modules': len(original) - 1}


def parse_boot_image(data):
    if len(data) < 4096 or data[:8] != b'ANDROID!' or struct.unpack_from('<I', data, 40)[0] != 0:
        raise Error('compatibility template must be an Android v0 boot image')
    kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, _, tags, page, _, os_version = struct.unpack_from('<10I', data, 8)
    if page != 4096 or second_size or kernel_size > len(data) - page:
        raise Error('invalid template kernel boundary or header')
    start = page + align(kernel_size, page)
    if start + ramdisk_size > len(data):
        raise Error('invalid template ramdisk boundary')
    try:
        decoder = zlib.decompressobj(31)
        combined = decoder.decompress(data[page:page + kernel_size], MAX_FV + 1)
    except zlib.error as error:
        raise Error(f'invalid template gzip stream: {error}') from error
    if not decoder.eof or len(combined) > MAX_FV or not decoder.unused_data:
        raise Error('invalid template firmware or appended device tree')
    if combined[56:60] != b'ARMd' or len(combined) < 192:
        raise Error('template ARM64 shim header missing')
    fv = combined.find(b'_FVH', 192)
    if fv < 40:
        raise Error('template firmware volume missing')
    shim, firmware = combined[:fv - 40], combined[fv - 40:]
    fv_files(firmware)
    version, patch = os_version >> 11, os_version & 2047
    image = {
        'header_version': 0, 'base': 0, 'kernel_offset': kernel_addr,
        'ramdisk_offset': ramdisk_addr, 'tags_offset': tags, 'pagesize': page,
        'encoded_os_version': os_version,
    }
    if version:
        image['os_version'] = f'{version >> 14}.{(version >> 7) & 127}.{version & 127}'
    if patch:
        if not 1 <= patch & 15 <= 12:
            raise Error('invalid template OS patch month')
        image['os_patch_level'] = f'{2000 + (patch >> 4):04d}-{patch & 15:02d}-01'
    return shim, firmware, decoder.unused_data, image


def template_file(ctx, spec):
    expected = spec.get('sha256', '')
    if len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
        raise Error('boot template requires a lowercase SHA-256 pin')
    override = os.environ.get('UNIXNU_BOOT_TEMPLATE')
    path = Path(override).expanduser() if override else ctx.out_root / 'downloads' / f'boot-template-{expected}.img.xz'
    if not path.is_file() and not override:
        url = spec.get('url', '')
        if not url.startswith('https://'):
            raise Error('boot template requires an HTTPS URL')
        path.parent.mkdir(parents=True, exist_ok=True)
        log('bootimg: downloading the pinned compatibility template')
        with tempfile.TemporaryDirectory(prefix='boot-template-', dir=path.parent) as temporary:
            candidate = Path(temporary) / 'template.img.xz'
            run([tool('curl'), '--fail', '--location', '--retry', '4', '--retry-all-errors', '--connect-timeout', '15',
                 '--max-time', '180', '--progress-bar', '--output', candidate, url])
            if sha256_file(candidate) != expected:
                raise Error('downloaded boot template checksum mismatch')
            candidate.replace(path)
    if not path.is_file() or sha256_file(path) != expected:
        raise Error(f'boot template is missing or has the wrong checksum: {path}')
    return path


def prepare(ctx, spec, source_firmware):
    path = template_file(ctx, spec)
    try:
        decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=MAX_FV * 2)
        data = decoder.decompress(path.read_bytes(), max_length=256 << 20)
        if not decoder.eof or decoder.unused_data:
            raise Error('boot template exceeds bounds or has trailing data')
    except lzma.LZMAError as error:
        raise Error(f'invalid boot template compression: {error}') from error
    shim, firmware, tree, image = parse_boot_image(data)
    if len(source_firmware) != len(firmware):
        raise Error('source and template firmware volumes have different sizes')
    identifier = str(uuid.UUID(spec['loader_guid']))
    pe = loader_pe(source_firmware, identifier)
    firmware, report = replace_loader(firmware, pe, identifier)
    report.update(template_sha256=sha256_file(path), source_fd_sha256=hashlib.sha256(source_firmware).hexdigest())
    return shim, firmware, tree, image, report
