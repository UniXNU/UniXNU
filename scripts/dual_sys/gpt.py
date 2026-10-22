"""Validate a conventional GPT and reserve the tail of userdata for UniXNU."""
import struct
import uuid
import zlib
from decimal import Decimal, InvalidOperation

MIB = 1 << 20
LINUX_DATA = uuid.UUID('0fc63daf-8483-4772-8e79-3d69d8477de4').bytes_le


def require(condition, message):
    if not condition:
        raise ValueError(message)


def size_bytes(value):
    try:
        size = Decimal(value) * (1 << 30)
        require(size.is_finite() and 0 < size < 1 << 63 and size % MIB == 0,
                'size must be positive GiB in whole MiB increments')
        return int(size)
    except InvalidOperation as exc:
        raise ValueError('invalid GiB size') from exc


def header(data, sector, lba, total):
    require(sector in (512, 4096) and len(data) == sector, 'unsupported sector size or short GPT header')
    values = struct.unpack_from('<8sIIIIQQQQ16sQIII', data)
    sig, version, length, crc, reserved, here, other, first, last, guid, table, count, width, table_crc = values
    require(sig == b'EFI PART' and version == 0x10000 and length == 92 and reserved == 0,
            'unsupported GPT header')
    check = bytearray(data[:length])
    struct.pack_into('<I', check, 16, 0)
    require(zlib.crc32(check) == crc, 'GPT header CRC mismatch')
    require(here == lba and other == (total - 1 if lba == 1 else 1), 'GPT disk geometry mismatch')
    require(width == 128 and 1 <= count <= 4096, 'unsupported GPT entry geometry')
    # GPT reserves at least 16 KiB even when the header declares fewer entries.
    blocks = (max(16384, count * width) + sector - 1) // sector
    require(table == (2 if lba == 1 else total - 1 - blocks), 'non-contiguous GPT tables are unsupported')
    require(2 + blocks <= first <= last < total - 1 - blocks, 'GPT usable range overlaps metadata')
    require(guid != bytes(16), 'missing GPT disk GUID')
    return dict(first=first, last=last, guid=guid, table=table, count=count, blocks=blocks, crc=table_crc)


def read_gpt(read, sector, total):
    """read(lba, count) returns exact raw logical sectors, without shell output."""
    h = header(read(1, 1), sector, 1, total)
    primary = read(0, 2 + h['blocks'])
    backup = read(total - 1 - h['blocks'], 1 + h['blocks'])
    return GPT(primary, backup, sector, total)


class GPT:
    def __init__(self, primary, backup, sector, total):
        self.sector, self.total = sector, total
        self.primary, self.backup = primary, backup
        h = header(primary[sector:2 * sector], sector, 1, total)
        b = header(backup[-sector:], sector, total - 1, total)
        require(len(primary) == (2 + h['blocks']) * sector and
                len(backup) == (1 + h['blocks']) * sector, 'short GPT regions')
        require(all(h[k] == b[k] for k in ('first', 'last', 'guid', 'count', 'blocks', 'crc')),
                'primary and backup GPT disagree')
        require(primary[510:512] == b'\x55\xaa', 'missing protective MBR')
        mbr_types = [primary[446 + i * 16 + 4] for i in range(4)]
        require(mbr_types.count(0xee) == 1 and all(t in (0, 0xee) for t in mbr_types),
                'hybrid or missing protective MBR')
        table = primary[2 * sector:2 * sector + h['count'] * 128]
        require(table == backup[:len(table)] and zlib.crc32(table) == h['crc'], 'GPT entry CRC or copy mismatch')
        self.h, self.table, self.entries = h, table, []
        for i in range(h['count']):
            entry = table[i * 128:(i + 1) * 128]
            if entry[:16] == bytes(16):
                require(entry == bytes(128), 'nonzero unused GPT entry')
                continue
            start, end, flags = struct.unpack_from('<QQQ', entry, 32)
            name = entry[56:128].decode('utf-16-le').split('\0', 1)[0]
            require(h['first'] <= start <= end <= h['last'], 'partition outside GPT usable range')
            require(entry[16:32] != bytes(16), 'missing partition GUID')
            self.entries.append(dict(index=i + 1, name=name, start=start, end=end, flags=flags,
                                     guid=str(uuid.UUID(bytes_le=entry[16:32]))))
        ordered = sorted(self.entries, key=lambda e: e['start'])
        require(all(a['end'] < b['start'] for a, b in zip(ordered, ordered[1:])), 'overlapping partitions')
        require(len({e['guid'] for e in ordered}) == len(ordered), 'duplicate partition GUIDs')

    def split(self, requested, userdata_index):
        require(requested > 0 and requested % MIB == 0, 'size must use whole MiB')
        require(not any(e['name'].lower() == 'unixnu' for e in self.entries), 'unixnu already exists; no resize performed')
        users = [e for e in self.entries if e['name'] == 'userdata']
        require(len(users) == 1 and users[0]['index'] == userdata_index, 'userdata identity does not match GPT')
        user = users[0]
        require(user['start'] * self.sector % 4096 == 0, 'userdata start must be aligned to an F2FS block')
        require(user['end'] == max(e['end'] for e in self.entries), 'userdata must be the last occupied partition')
        used = {e['index'] for e in self.entries}
        empty = next((i for i in range(1, self.h['count'] + 1) if i not in used), None)
        require(empty is not None, 'no free GPT entry')
        align = MIB // self.sector
        end = (user['end'] + 1) // align * align - 1
        start = end + 1 - requested // self.sector
        require(start > user['start'] and (start - user['start']) * self.sector >= MIB,
                'requested size leaves no usable userdata')
        table = bytearray(self.table)
        struct.pack_into('<Q', table, (userdata_index - 1) * 128 + 40, start - 1)
        entry = bytearray(128)
        entry[:16], entry[16:32] = LINUX_DATA, uuid.uuid4().bytes_le
        struct.pack_into('<QQQ', entry, 32, start, end, 0)
        entry[56:68] = 'unixnu'.encode('utf-16-le')
        table[(empty - 1) * 128:empty * 128] = entry
        primary, backup = bytearray(self.primary), bytearray(self.backup)
        primary[2 * self.sector:2 * self.sector + len(table)] = table
        backup[:len(table)] = table
        for region, offset in ((primary, self.sector), (backup, len(backup) - self.sector)):
            struct.pack_into('<I', region, offset + 88, zlib.crc32(table))
            struct.pack_into('<I', region, offset + 16, 0)
            struct.pack_into('<I', region, offset + 16, zlib.crc32(region[offset:offset + 92]))
        GPT(bytes(primary), bytes(backup), self.sector, self.total)
        return bytes(primary), bytes(backup), dict(
            userdata_index=userdata_index, unixnu_index=empty, userdata_start=user['start'],
            userdata_end=start - 1, unixnu_start=start, unixnu_end=end,
            old_userdata_bytes=(user['end'] - user['start'] + 1) * self.sector,
            new_userdata_bytes=(start - user['start']) * self.sector,
            unixnu_bytes=requested, tail_gap_bytes=(user['end'] - end) * self.sector)
