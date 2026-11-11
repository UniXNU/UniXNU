#!/usr/bin/env python3
"""Unpack an Android boot image header v0-v2 into kernel/ramdisk/second/dtb + header.txt."""
import struct, sys, os
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
b = open(src, 'rb').read()
assert b[:8] == b'ANDROID!'
(ks, ka, rs, ra, ss, sa, ta, ps, ver, osv) = struct.unpack_from('<10I', b, 8)
cmd = b[64:64+512].split(b'\0')[0] + b[608:608+1024].split(b'\0')[0]
info = dict(kernel_size=ks, kernel_addr=hex(ka), ramdisk_size=rs, ramdisk_addr=hex(ra),
            second_size=ss, tags_addr=hex(ta), page_size=ps, header_version=ver,
            os_version=hex(osv), name=b[48:64].split(b'\0')[0].decode(), cmdline=cmd.decode())
rnd = lambda n: (n + ps - 1) // ps * ps
off = ps
parts = [('kernel', ks), ('ramdisk', rs), ('second', ss)]
if ver >= 1:
    rds, rdo, hs = struct.unpack_from('<IQI', b, 1632)
    parts.append(('recovery_dtbo', rds)); info['header_size'] = hs
if ver >= 2:
    ds, da = struct.unpack_from('<IQ', b, 1648)
    parts.append(('dtb', ds)); info['dtb_addr'] = hex(da)
for name, sz in parts:
    if sz:
        open(f'{out}/{name}', 'wb').write(b[off:off+sz])
    info[name + '_offset'] = off
    off += rnd(sz)
with open(f'{out}/header.txt', 'w') as f:
    for k, v in info.items():
        f.write(f'{k}: {v}\n')
print(open(f'{out}/header.txt').read())
