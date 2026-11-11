#!/usr/bin/env python3
"""Apple Device Tree (ADT) tools.

  adt.py dump FILE [--hex]      FILE = raw ADT or an IM4P-wrapped DeviceTree
  adt.py unwrap IM4P OUT        write the raw IM4P payload

ADT layout: node = {u32 nprops, u32 nchildren, props..., children...};
prop = {char name[32], u32 size (bit31 = placeholder flag), value padded to 4}.
"""
import struct, subprocess, sys


def der(buf, off):
    """Return (tag, value_start, value_end) for the DER element at off."""
    tag = buf[off]
    ln = buf[off + 1]
    off += 2
    if ln & 0x80:
        n = ln & 0x7f
        ln = int.from_bytes(buf[off:off + n], 'big')
        off += n
    return tag, off, off + ln


def im4p_payload(buf):
    tag, s, e = der(buf, 0)
    assert tag == 0x30, 'not a DER sequence'
    items, off = [], s
    while off < e:
        t, vs, ve = der(buf, off)
        items.append((t, buf[vs:ve]))
        off = ve
    assert items[0][1] == b'IM4P', items[0]
    # optional trailing items: KBAG (OCTET STRING) = encrypted, SEQUENCE = compression info
    info = {'type': items[1][1].decode(), 'desc': items[2][1].decode(),
            'encrypted': any(t == 0x04 for t, _ in items[4:])}
    payload = items[3][1]
    if payload[:4] == b'bvx2':
        payload = subprocess.run(['lzfse', '-decode'], input=payload,
                                 capture_output=True, check=True).stdout
    return payload, info


def load(path):
    buf = open(path, 'rb').read()
    if buf[:1] == b'\x30' and b'IM4P' in buf[:16]:
        buf, info = im4p_payload(buf)
        assert not info['encrypted'], 'payload is encrypted (KBAG present)'
    return buf


class Node:
    def __init__(self):
        self.props = []		# (name, flags, bytes)
        self.children = []

    @property
    def name(self):
        for n, _, v in self.props:
            if n == 'name':
                return v.split(b'\0')[0].decode()
        return '?'

    def prop(self, name):
        for n, _, v in self.props:
            if n == name:
                return v
        return None


def parse(buf, off=0):
    node = Node()
    nprops, nchildren = struct.unpack_from('<II', buf, off)
    off += 8
    for _ in range(nprops):
        name = buf[off:off + 32].split(b'\0')[0].decode()
        size, = struct.unpack_from('<I', buf, off + 32)
        flags, ln = size >> 31, size & 0x7fffffff
        node.props.append((name, flags, buf[off + 36:off + 36 + ln]))
        off += 36 + ((ln + 3) & ~3)
    for _ in range(nchildren):
        child, off = parse(buf, off)
        node.children.append(child)
    return node, off


def serialize(node):
    out = bytearray(struct.pack('<II', len(node.props), len(node.children)))
    for name, flags, val in node.props:
        out += name.encode().ljust(32, b'\0')[:32]
        out += struct.pack('<I', len(val) | (flags << 31))
        out += val + b'\0' * (-len(val) & 3)
    for c in node.children:
        out += serialize(c)
    return bytes(out)


def fmt(v, hexall=False):
    if v and v[-1:] == b'\0' and all(32 <= c < 127 for c in v[:-1].replace(b'\0', b' ')) and len(v) > 1:
        return repr(v.rstrip(b'\0').replace(b'\0', b'|').decode())
    if len(v) in (4, 8) and not hexall:
        return hex(int.from_bytes(v, 'little'))
    if len(v) % 8 == 0 and len(v) <= 64:
        return '<' + ' '.join(hex(x) for x in struct.unpack('<%dQ' % (len(v) // 8), v)) + '>'
    if len(v) % 4 == 0 and len(v) <= 64:
        return '<' + ' '.join(hex(x) for x in struct.unpack('<%dI' % (len(v) // 4), v)) + '>'
    return v[:48].hex() + ('...' if len(v) > 48 else '') + f' ({len(v)} bytes)'


def dump(node, depth=0, hexall=False):
    ind = '  ' * depth
    print(f'{ind}{node.name} {{')
    for n, flags, v in node.props:
        if n == 'name':
            continue
        print(f'{ind}  {n}{" [placeholder]" if flags else ""} = {fmt(v, hexall)}')
    for c in node.children:
        dump(c, depth + 1, hexall)
    print(f'{ind}}}')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'dump':
        root, end = parse(load(sys.argv[2]))
        dump(root, hexall='--hex' in sys.argv)
    elif cmd == 'unwrap':
        open(sys.argv[3], 'wb').write(load(sys.argv[2]))
