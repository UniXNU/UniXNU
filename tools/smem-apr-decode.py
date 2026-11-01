#!/usr/bin/env python3
"""Decode APR packets left in the APPS<->ADSP GLINK FIFOs of an SMEM dump.

  tools/smem-apr-decode.py SMEM.bin [HOST]

SMEM.bin is the 2 MiB SMEM region (0x80900000 on SM8250) read from a running system. HOST is the remote's SMEM
host id (ADSP 2). The FIFOs are rings: each is printed from the oldest byte (just past the head) to the newest,
and every APR header found in it (version 0, 5- or 8-word header, APPS domain 5 <-> ADSP domain 4) is decoded.
Layouts as sweet_slpi.c (Linux smem.c / qcom_glink_smem.c).
"""
import struct
import sys

blob = open(sys.argv[1], 'rb').read()
host = int(sys.argv[2]) if len(sys.argv) > 2 else 2
u16 = lambda o: struct.unpack_from('<H', blob, o)[0]
u32 = lambda o: struct.unpack_from('<I', blob, o)[0]

toc = len(blob) - 0x1000
assert blob[toc:toc + 4] == b'$TOC', 'no SMEM partition table'
items = {}
for i in range(min(u32(toc + 8), 64)):
    e = toc + 32 + 48 * i
    h0, h1 = u16(e + 12), u16(e + 14)
    if {h0, h1} != {0, host}:
        continue
    p = u32(e)
    assert blob[p:p + 4] == b'$PRT'
    end = p + u32(p + 12)
    q = p + 32
    while q + 16 <= end and u16(q) == 0xa5a5:
        item, size, pad_data, pad_hdr = u16(q + 2), u32(q + 4), u16(q + 8), u16(q + 10)
        items[item] = (q + 16 + pad_hdr, size - pad_data)
        q += 16 + pad_hdr + size
print('items in the 0-%d partition:' % host, sorted(items))

desc = items[478][0]
tx_tail, tx_head, rx_tail, rx_head = (u32(desc + 4 * k) for k in range(4))
print('descriptor: tx tail %d head %d, rx tail %d head %d' % (tx_tail, tx_head, rx_tail, rx_head))

SVC = {3: 'CORE', 4: 'AFE', 7: 'ASM', 8: 'ADM', 9: 'MVM', 10: 'CVS', 11: 'CVP'}


def ring(item, head):
    off, size = items[item]
    data = blob[off:off + size]
    return data[head:] + data[:head]        # oldest first


def apr_scan(data, label, want_src):
    n = 0
    for i in range(0, len(data) - 20, 4):
        hf, psize = struct.unpack_from('<HH', data, i)
        if hf & 0xf or (hf >> 4) & 0xf not in (5, 8) or psize < 20 or psize > 4096:
            continue
        ssvc, sdom, sport, dsvc, ddom, dport, token, op = struct.unpack_from('<BBHBBHII', data, i + 4)
        if (sdom, ddom) != want_src or op == 0 or op > 0x7fffffff:
            continue
        hlen = ((hf >> 4) & 0xf) * 4
        pl = data[i + hlen:i + min(psize, 96)]
        words = ' '.join('%08x' % w for w in struct.unpack_from('<%dI' % (len(pl) // 4), pl)) if len(pl) >= 4 else ''
        print('%s @%5d hdr %#06x size %3d %s(%d)->%s(%d) port %#x->%#x token %#x opcode %#010x: %s' % (
            label, i, hf, psize, SVC.get(ssvc, ssvc), sdom, SVC.get(dsvc, dsvc), ddom, sport, dport, token, op, words))
        n += 1
    return n


print('--- APPS -> ADSP (item 479, oldest first) ---')
apr_scan(ring(479, tx_head), 'TX', (5, 4))
print('--- ADSP -> APPS (item 480, oldest first) ---')
apr_scan(ring(480, rx_head), 'RX', (4, 5))
