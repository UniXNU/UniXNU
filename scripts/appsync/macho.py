"""Route Foundation through an adapter that re-exports it, without moving code.

Only the Foundation dependency's name is changed. Chained fixups, authenticated
pointers, instructions, sections and the original code signature stay in place;
the caller must re-sign the resulting copy.
"""
import hashlib
import struct


def add_dylib(data, name, expected_sha256):
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError('OS executable does not match the 24A446 source pin')
    if len(data) < 32:
        raise ValueError('truncated Mach-O header')
    magic, cpu, subtype, kind, count, size = struct.unpack_from('<6I', data)
    if (magic, cpu, subtype, kind) != (0xfeedfacf, 0x100000c, 0x80000002, 2):
        raise ValueError('expected an arm64e MH_EXECUTE image')
    end = 32 + size
    if end > len(data):
        raise ValueError('truncated load commands')
    at, replacements = 32, []
    foundation = b'/System/Library/Frameworks/Foundation.framework/Foundation'
    for _ in range(count):
        if at + 8 > end:
            raise ValueError('truncated load command')
        command, length = struct.unpack_from('<II', data, at)
        if length < 8 or length % 8 or at + length > end:
            raise ValueError('invalid load command size')
        if command in (0xc, 0x80000018, 0x8000001f, 0x80000023):
            if length < 24:
                raise ValueError('truncated dependency')
            offset = struct.unpack_from('<I', data, at + 8)[0]
            if not 24 <= offset < length:
                raise ValueError('invalid dependency name offset')
            if data[at + offset:at + length].split(b'\0', 1)[0] == name.encode():
                raise ValueError('dependency already present')
            if data[at + offset:at + length].split(b'\0', 1)[0] == foundation:
                if command != 0xc:
                    raise ValueError('Foundation is not a required dependency')
                replacements.append((at + offset, length - offset))
        at += length
    if at != end:
        raise ValueError('load command count differs from size')
    raw = name.encode() + b'\0'
    if len(replacements) != 1:
        raise ValueError('expected exactly one Foundation dependency')
    start, length = replacements[0]
    if len(raw) > length:
        raise ValueError('adapter path does not fit the dependency command')
    result = bytearray(data)
    result[start:start + length] = raw.ljust(length, b'\0')
    return bytes(result)
