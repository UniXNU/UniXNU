#!/usr/bin/env python3
"""Print what a payload's device tree asks of the loader: the darwinboot-* properties of /chosen.

    adt-chosen.py ADT

ADT is the kernel.macho.adt of a payload volume (mcopy -i payload.img ::/EFI/UniXNU/Payloads/kernel.macho.adt .).
One line per property, in the tree's order: "<name> <length> <value>". An 8-byte value is printed as one number.
A value of whole 16-byte pairs is printed as "N empty pairs" when all of it is zero (a table the loader fills),
otherwise as its (base, size) pairs "0xBASE+0xSIZE". Any other value is printed as hexadecimal digits.

Used to check a built payload before it goes to the tablet: the window's size and floor, the sizes of the tables and
the ranges the kernel must leave alone. A file that is not one whole device tree, or has no /chosen, is refused.
"""
import struct
import sys
from pathlib import Path

REFUSAL = 'adt-chosen: '


class Malformed(Exception):
    pass


def read_node(blob, at, depth=0):
    """(properties as (name, value, offset of the value in blob) in order, children as the same tuples, offset behind the node)"""
    if depth > 64 or len(blob) - at < 8:
        raise Malformed('a node is cut off')
    count, children = struct.unpack_from('<II', blob, at)
    at += 8
    properties = []
    for _ in range(count):
        if len(blob) - at < 36:
            raise Malformed('a property is cut off')
        name, length = struct.unpack_from('<32sI', blob, at)
        length &= 0x7fffffff  # the top bit is a flag of the format, not part of the length
        at += 36
        if length > len(blob) - at:
            raise Malformed('a property value is cut off')
        properties.append((name.split(b'\0', 1)[0].decode('ascii', 'replace'), blob[at:at + length], at))
        at += length + (-length % 4)
        if at > len(blob):
            raise Malformed('the padding of a property is cut off')
    nodes = []
    for _ in range(children):
        child, at = read_node(blob, at, depth + 1)
        nodes.append(child)
    return (properties, nodes), at


def find_chosen(blob):
    """The /chosen node of a blob that is exactly one device tree."""
    root, end = read_node(blob, 0)
    if end != len(blob):
        raise Malformed(f'{len(blob) - end} bytes behind the root node')
    chosen = [child for child in root[1] if dict((name, value) for name, value, _ in child[0]).get('name') == b'chosen\0']
    if len(chosen) != 1:
        raise Malformed(f'{len(chosen)} /chosen nodes')
    return chosen[0]


def describe(value):
    if len(value) == 8:
        return f'{struct.unpack("<Q", value)[0]:#x}'
    if value and len(value) % 16 == 0:
        pairs = [struct.unpack_from('<QQ', value, offset) for offset in range(0, len(value), 16)]
        if not any(value):
            return f'{len(pairs)} empty pairs'
        return ' '.join(f'{base:#x}+{size:#x}' for base, size in pairs)
    return value.hex() or '-'


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    try:
        chosen = find_chosen(path.read_bytes())
    except (OSError, Malformed) as error:
        sys.exit(f'{REFUSAL}{path}: {error}')
    for name, value, _ in chosen[0]:
        if name.startswith('darwinboot-'):
            print(name, len(value), describe(value))


if __name__ == '__main__':
    main()
