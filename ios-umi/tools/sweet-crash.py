#!/usr/bin/env python3
"""Symbolicate SWEET console crash reports (patch 0043) typed in from a photo.

  sweet-crash.py CACHE ROOT [REPORT.txt]       (report on stdin if omitted)

CACHE is the dyld_shared_cache_arm64 (in a writable directory: ipsw keeps a
symbol cache next to it), ROOT the mounted iOS root image. Lines look like

  CRASH name[pid] sig 6 code 0x... sub 0x... slide 0x... mh 0x...
  CRASH name pc 0x... lr 0x... sp 0x... fp 0x... far 0x...
  CRASH name bt 0x... 0x... ...

Addresses inside the shared cache are unslid (addr - slide) and resolved
with `ipsw dyld a2s`; addresses in the main binary are shown as offsets
from its Mach-O header (address - mh + 0x100000000, the binary's own
vmaddr) for llvm-objdump of ROOT's executable.
"""
import re, subprocess, sys

CACHE_LO, CACHE_HI = 0x180000000, 0x300000000


def a2s(cache, addr):
    r = subprocess.run(['ipsw', 'dyld', 'a2s', cache, hex(addr)], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith('0x')]
    return lines[-1].split(': ', 1)[1] if lines else '?'


def main():
    cache = sys.argv[1]
    text = open(sys.argv[3]).read() if len(sys.argv) > 3 else sys.stdin.read()
    slide = mh = 0
    for line in text.splitlines():
        m = re.search(r'slide (0x[0-9a-f]+) mh (0x[0-9a-f]+)', line)
        if m:
            slide, mh = int(m.group(1), 16), int(m.group(2), 16)
            print(line)
            continue
        print(line)
        for a in re.findall(r'(?:pc|lr|bt|\s)(?: )?(0x[0-9a-f]{6,})', line):
            v = int(a, 16)
            if CACHE_LO <= v - slide < CACHE_HI:
                print(f'    {a} = cache {hex(v - slide)} {a2s(cache, v - slide)}')
            elif mh and mh <= v < mh + 0x10000000:
                print(f'    {a} = main binary {hex(v - mh + 0x100000000)}')


if __name__ == '__main__':
    main()
