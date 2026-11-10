#!/usr/bin/env python3
"""Bind a Mach-O image's weak flat-namespace imports to the image itself.

    self-bind-weak-imports.py IMAGE

Mesa takes the address of every Vulkan entry point a driver may implement through weak declarations. The ones the driver
leaves out stay undefined, and with -undefined dynamic_lookup the linker records each as a weak import looked up in the flat
namespace: at load dyld searches every image of the process for each name before it settles on NULL. Bound to the image
itself, dyld reads the image's own export trie, which holds none of them, and leaves each NULL as before.

Only imports of the chained fixups (LC_DYLD_CHAINED_FIXUPS) that are both weak and flat are changed; the image must be signed
after this. Running it again changes nothing."""
import struct
import sys

LC_DYLD_CHAINED_FIXUPS = 0x80000034
MH_MAGIC_64 = 0xfeedfacf
path = sys.argv[1]
data = bytearray(open(path, 'rb').read())
if struct.unpack_from('<I', data, 0)[0] != MH_MAGIC_64:
    sys.exit(path + ': not a thin 64-bit Mach-O image')
commands = struct.unpack_from('<I', data, 16)[0]
at, fixups = 32, None
for _ in range(commands):
    command, size = struct.unpack_from('<II', data, at)
    if command == LC_DYLD_CHAINED_FIXUPS:
        fixups = struct.unpack_from('<I', data, at + 8)[0]
    at += size
if fixups is None:
    sys.exit(path + ': no chained fixups')
_, _, imports, _, count, form, _ = struct.unpack_from('<7I', data, fixups)
# DYLD_CHAINED_IMPORT (1) and _ADDEND (2): ordinal in bits 0-7, weak in bit 8. _ADDEND64 (3): ordinal in bits 0-15, weak in bit 16.
size, ordinal_bits = {1: (4, 8), 2: (8, 8), 3: (16, 16)}[form]
mask, flat = (1 << ordinal_bits) - 1, (1 << ordinal_bits) - 2
changed = 0
for index in range(count):
    where = fixups + imports + index * size
    word = struct.unpack_from('<I', data, where)[0]
    if word & mask == flat and word >> ordinal_bits & 1:
        struct.pack_into('<I', data, where, word & ~mask)   # ordinal 0: this image
        changed += 1
open(path, 'wb').write(data)
print('%s: %d weak flat-namespace imports bound to the image' % (path, changed))
