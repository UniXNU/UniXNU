#!/usr/bin/env python3
"""Compare pointer probe CSVs (local-tools/tablet-pointer-probe.js) for the jump after a pause.

    pointer-csv-stats.py CSV [CSV ...] [--pause MS] [--big PX]

Each CSV line is one position change: milliseconds since the first movement, x, y. For every step this takes the time since
the change before it (the gap) and the angle to the step before that pause. The cover's lost-lift jump is a large step right
after a still period (gap at least --pause ms) whose direction has nothing to do with the motion before it. A fast swipe
gives large steps with short gaps that keep their direction.
"""
import argparse
import math
from pathlib import Path


def load(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        parts = line.split(',')
        if len(parts) == 3:
            rows.append((float(parts[0]), float(parts[1]), float(parts[2])))
    return rows


def angle(a, b):
    na, nb = math.hypot(*a), math.hypot(*b)
    if not na or not nb:
        return None
    cos = max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (na * nb)))
    return math.degrees(math.acos(cos))


def pct(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(q * len(values)))] if values else 0


def report(path, pause, big):
    rows = load(path)
    steps = []
    for i in range(1, len(rows)):
        t0, x0, y0 = rows[i - 1]
        t1, x1, y1 = rows[i]
        steps.append({'t': t1, 'gap': t1 - t0, 'd': (x1 - x0, y1 - y0), 'len': math.hypot(x1 - x0, y1 - y0)})
    for i, s in enumerate(steps):
        s['turn'] = angle(steps[i - 1]['d'], s['d']) if i else None
    after_pause = [s for s in steps if s['gap'] >= pause]
    moving = [s for s in steps if s['gap'] < pause]
    print(f'{path}: {len(rows)} positions over {rows[-1][0] / 1000:.1f} s')
    print(f'  moving steps (gap < {pause:.0f} ms): {len(moving)}, length median {pct([s["len"] for s in moving], .5):.0f} px, '
          f'p90 {pct([s["len"] for s in moving], .9):.0f}, max {max((s["len"] for s in moving), default=0):.0f}; '
          f'gap median {pct([s["gap"] for s in moving], .5):.0f} ms')
    print(f'  first steps after a pause (gap >= {pause:.0f} ms): {len(after_pause)}, length median '
          f'{pct([s["len"] for s in after_pause], .5):.0f} px, max {max((s["len"] for s in after_pause), default=0):.0f}; '
          f'over {big:.0f} px: {sum(s["len"] > big for s in after_pause)}')
    for s in after_pause:
        if s['len'] > big:
            turn = 'n/a' if s['turn'] is None else f'{s["turn"]:.0f} deg'
            print(f'    at {s["t"]:.0f} ms: {s["len"]:.0f} px after {s["gap"]:.0f} ms still, turn {turn}')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('csv', nargs='+')
    parser.add_argument('--pause', type=float, default=60.0)
    parser.add_argument('--big', type=float, default=150.0)
    args = parser.parse_args()
    for path in args.csv:
        report(path, args.pause, args.big)


if __name__ == '__main__':
    main()
