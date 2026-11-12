"""SHNGDATA container storage and offline addon installation."""
import errno
import hashlib
import json
import os
from pathlib import Path
import struct
import zlib

PAGE = 4096


def empty_seed(logical):
    if logical <= 2 << 30 or logical % PAGE:
        raise ValueError('container must be larger than 2 GiB and page aligned')
    return struct.pack('<8sIIQQ', b'DBRDISK1', 1, PAGE, logical, 0)


def seed_digest(logical):
    empty_seed(logical)
    return hashlib.sha256(b'SHNGSEED2' + struct.pack('<Q', logical)).hexdigest()


def header(pages, digest, generation=1):
    block = bytearray(PAGE)
    block[:8] = b'SHNGDATA'
    struct.pack_into('<IIQ', block, 8, 1, 64, pages)
    block[24:56] = bytes.fromhex(digest)
    struct.pack_into('<I', block, 56, generation)
    struct.pack_into('<I', block, 60, zlib.crc32(block[:60]))
    return block


def data_ranges(handle, start, end):
    """Allocated file ranges, or a bounded sequential fallback on filesystems without SEEK_DATA."""
    cursor = start
    while cursor < end:
        try:
            first = os.lseek(handle.fileno(), cursor, os.SEEK_DATA)
            if first >= end:
                return
            last = min(os.lseek(handle.fileno(), first, os.SEEK_HOLE), end)
        except OSError as error:
            if error.errno == errno.ENXIO:
                return
            if error.errno not in (errno.EINVAL, errno.ENOTSUP):
                raise
            yield cursor, end
            return
        yield max(first, start), last
        cursor = last


def mark_data(path, offset, logical, store_offset=0):
    pages = logical // PAGE
    bits = bytearray(((pages + PAGE * 8 - 1) // (PAGE * 8)) * PAGE)
    with open(path, 'r+b') as handle:
        for first, last in data_ranges(handle, offset, offset + logical):
            for page in range((first - offset) // PAGE, (last - offset + PAGE - 1) // PAGE):
                bits[page // 8] |= 1 << (page % 8)
        handle.seek(store_offset + PAGE)
        handle.write(bits)
        handle.flush()
        os.fsync(handle.fileno())
    return sum(byte.bit_count() for byte in bits)


def copy_sparse(source, target, offset):
    with open(source, 'rb', buffering=0) as handle:
        for first, last in data_ranges(handle, 0, os.fstat(handle.fileno()).st_size):
            handle.seek(first)
            target.seek(offset + first)
            while first < last:
                data = handle.read(min(8 << 20, last - first))
                if not data:
                    raise ValueError('short container store read')
                target.write(data)
                first += len(data)


def read_layout(directory, expected_uuid=None, expected_gib=None, expected_source_uuid=None):
    directory = Path(directory)
    layout = json.loads((directory / 'disk.json').read_text())
    logical = layout['bytes']
    if layout.get('format') != 'UniXNU.NativeAPFS.v1':
        raise ValueError('unsupported container layout')
    if expected_uuid and layout['system']['uuid'].upper() != expected_uuid.upper():
        raise ValueError('System UUID does not match the selected IPSW root')
    if expected_source_uuid and layout.get('source_system_uuid', '').upper() != expected_source_uuid.upper():
        raise ValueError('IPSW System UUID does not match the selected source')
    if expected_gib and logical != expected_gib << 30:
        raise ValueError('container size does not match the board runtime')
    # The seed has no extents. All initial APFS content resides in the persistent store.
    if (directory / 'scratch-data.img').read_bytes() != empty_seed(logical):
        raise ValueError('container requires its empty packed seed')
    pages = logical // PAGE
    offset = (1 + (pages + PAGE * 8 - 1) // (PAGE * 8)) * PAGE
    store = directory / 'data-store.img'
    base = layout.get('store_offset', 0)
    if base < 0 or base % PAGE:
        raise ValueError('container store offset is invalid')
    if store.stat().st_size != base + offset + logical or layout['window_offset'] != offset:
        raise ValueError('container store size or page offset mismatch')
    with store.open('rb') as handle:
        handle.seek(base)
        block = handle.read(PAGE)
        if block != header(pages, seed_digest(logical)):
            raise ValueError('container store header does not match its seed')
        # Root metadata must come from the installed container, never an empty fallback.
        bit0 = handle.read(1)
        handle.seek(base + offset + 32)
        if not bit0 or not bit0[0] & 1 or handle.read(4) != b'NXSB':
            raise ValueError('container superblock is absent')
    for role in ('data', 'preboot', 'vm', 'update', 'hardware', 'xart'):
        if not layout.get(role, {}).get('uuid'):
            raise ValueError(f'missing {role} volume')
    return layout


def addon_entries(path):
    data = Path(path).read_bytes()
    if len(data) < 24 or data[:8] != b'NGPUADD2' or struct.unpack_from('<Q', data, 16)[0] != len(data):
        raise ValueError('invalid runtime addon')
    count, at = struct.unpack_from('<I', data, 8)[0], 24
    entries = []
    for _ in range(count):
        length, mode, size, packed = struct.unpack_from('<IIQQ', data, at)
        at += 24
        raw = data[at:at + length]
        name = raw[:-1].decode()
        if not 1 < length <= 160 or not raw.endswith(b'\0') or '\0' in name or name.startswith('/') or '..' in Path(name).parts:
            raise ValueError('invalid addon path')
        at += (length + 7) & ~7
        body = zlib.decompress(data[at:at + packed])
        at += (packed + 7) & ~7
        if len(body) != size:
            raise ValueError('invalid addon file size')
        entries.append((name, mode & 0o777, body))
    if at != len(data):
        raise ValueError('invalid addon trailing bytes')
    return entries


def addon_path(name, system):
    if system:
        # Native launchd jobs and dyld use the standard System paths directly.
        for prefix, target in (('GPUBundles/', 'System/Library/Extensions/'), ('sbin/', 'usr/sbin/'), ('lib/', 'usr/lib/')):
            if name.startswith(prefix):
                return target + name[len(prefix):]
        return None
    if name.startswith('Library/'):
        return name
    if name.startswith('GPUBundles/'):
        return 'Library/' + name
    return 'private/var/ngpu/' + name


def install_addon(path, mount, system):
    mount = Path(mount).resolve()
    for name, mode, body in addon_entries(path):
        relative = addon_path(name, system)
        if relative is None:
            continue
        target = mount / relative
        # Do not follow template symlinks outside the mounted volume.
        if not target.parent.resolve().is_relative_to(mount):
            raise ValueError(f'addon destination escapes volume: {relative}')
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            target.unlink()
        target.write_bytes(body)
        target.chmod(mode)
        os.chown(target, 0, 0)


def bind_payload(ctx):
    spec = ctx.board.get('payload', {}).get('runtime', {})
    if not spec.get('container_layout'):
        return
    directory = getattr(ctx.args, 'apfs_container', None)
    if not directory:
        raise ValueError('native APFS payload requires --apfs-container DIR')
    layout = read_layout(directory, expected_gib=spec['data_gib'],
                         expected_source_uuid=ctx.board['userdata'].get('source_system_uuid'))
    identity = layout['system']['uuid']
    ctx.board['payload'].setdefault('adt', {})['root_match_volume_uuid'] = identity
    chosen = ctx.board.setdefault('adt', {}).setdefault('chosen', {}).setdefault('string', {})
    chosen['boot-uuid'] = chosen['apfs-preboot-uuid'] = identity
    ctx.args.data_ramdisk = str(Path(directory).expanduser().resolve() / 'scratch-data.img')


def apfs_checksum(data):
    """Fletcher checksum of an APFS object, excluding its first eight bytes."""
    lo = hi = 0
    for (word,) in struct.iter_unpack('<I', data):
        lo = (lo + word) % 0xffffffff
        hi = (hi + lo) % 0xffffffff
    first = 0xffffffff - ((lo + hi) % 0xffffffff)
    second = 0xffffffff - ((lo + first) % 0xffffffff)
    return struct.pack('<II', first, second)


def mark_empty_xart(path, offset, logical, identity):
    """Set only the role and checksum of a newly created, unmounted empty volume."""
    import uuid
    identity = uuid.UUID(identity).bytes
    changes = []
    with open(path, 'r+b', buffering=0) as handle:
        for first, last in data_ranges(handle, offset, offset + logical):
            handle.seek(first)
            cursor = first
            while cursor < last:
                chunk = handle.read(min(8 << 20, last - cursor))
                if not chunk:
                    raise ValueError('short container read during xART marking')
                at = chunk.find(b'APSB')
                while at >= 0:
                    start = at - 32
                    if (start >= 0 and (cursor + start - offset) % PAGE == 0 and start + PAGE <= len(chunk)):
                        block = bytearray(chunk[start:start + PAGE])
                        if (block[240:256] == identity and struct.unpack_from('<I', block, 24)[0] & 0xffff == 0xd
                                and apfs_checksum(block[8:]) == block[:8]):
                            role = struct.unpack_from('<H', block, 964)[0]
                            counts = struct.unpack_from('<5Q', block, 184)
                            if role != 0 or counts[0] or counts[1] > 1 or any(counts[2:]):
                                raise ValueError('xART marking requires a new empty, unroled volume')
                            struct.pack_into('<H', block, 964, 0x100)
                            block[:8] = apfs_checksum(block[8:])
                            changes.append((cursor + start, bytes(block)))
                    at = chunk.find(b'APSB', at + 4)
                cursor += len(chunk)
        if not changes or len(changes) > 512:
            raise ValueError('could not identify the empty xART volume superblocks')
        for position, block in changes:
            handle.seek(position)
            handle.write(block)
        handle.flush()
        os.fsync(handle.fileno())
    return len(changes)
