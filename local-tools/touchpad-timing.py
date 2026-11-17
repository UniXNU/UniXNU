#!/usr/bin/env python3
"""Decode the cover's ShengTouchpadTiming record (UniXNU-sheng KeyboardCover.cpp, layout 1) from `ioreg` output.

    ssh <tablet> 'ioreg -r -c ShengKeyboardCover -d 1' | touchpad-timing.py [--since EARLIER_HEX]

Words (32-bit little-endian): layout, touchpad reports, pointer reports sent, touches the 60 ms rule restarted, eight gap buckets
(gaps before reports that follow one with a finger down: under 10, 20, 30, 45, 60, 100, 250 ms, then the rest), then the 17
native_keyboard_stats counters. With --since, the counts are shown as the difference from an earlier record.
"""
import argparse
import re
import struct
import sys

BUCKETS = ['<10', '10-20', '20-30', '30-45', '45-60', '60-100', '100-250', '>=250']
STATS = ['stage', 'detail', 'engine', 'rom', 'load ms', 'interrupts', 'frames', 'reports passed', 'attach', 'hall', 'input on',
         'i2c failures', 'engine interrupts', 'last i2c error', 'commands', 'auth|other', 'palms lifted']


def words(text):
    match = re.search(r'"ShengTouchpadTiming" = <([0-9a-fA-F]+)>', text) or re.fullmatch(r'\s*<?([0-9a-fA-F]+)>?\s*', text)
    if not match:
        raise SystemExit('no ShengTouchpadTiming record in the input')
    raw = bytes.fromhex(match.group(1))
    values = list(struct.unpack(f'<{len(raw) // 4}I', raw[:len(raw) // 4 * 4]))
    if values[0] != 1 or len(values) != 4 + len(BUCKETS) + len(STATS):
        raise SystemExit(f'unknown layout {values[0]} with {len(values)} words')
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--since', help='an earlier record, as the hex between < and >')
    args = parser.parse_args()
    now = words(sys.stdin.read())
    base = words(args.since) if args.since else [0] * len(now)
    d = [a - b for a, b in zip(now, base)]
    print(f'touchpad reports {d[1]}, pointer reports sent {d[2]}, restarts by the 60 ms rule {d[3]}')
    gaps = d[4:4 + len(BUCKETS)]
    total = sum(gaps) or 1
    print('gaps with a finger down: ' + ', '.join(f'{b} ms {g} ({100 * g / total:.0f}%)' for b, g in zip(BUCKETS, gaps)))
    stats = now[4 + len(BUCKETS):]
    delta = d[4 + len(BUCKETS):]
    print(f'controller: stage {stats[0]}, interrupts +{delta[5]}, frames +{delta[6]}, i2c failures {stats[11]} (+{delta[11]}), '
          f'last i2c error {stats[13]:#x}, attached {stats[8] & 0xff} after {(stats[8] >> 8) & 0xffff} attaches, '
          f'auth {stats[15] & 0xffff}, other frames {stats[15] >> 16}, commands {stats[14]}')


if __name__ == '__main__':
    main()
