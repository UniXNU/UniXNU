#!/usr/bin/env python3
"""Decode patch 0180's COPY-path pixel logs, without hiding missing UDP records.

Usage: umi-fb-copydump.py LIVE_LOG OUTPUT_DIRECTORY
Writes RGB and alpha PNGs for each captured rectangle, plus report.json with
geometry, row profiles and packet coverage. Missing pixels are magenta in RGB
and zero in alpha. Input words are little-endian BGRA8888 (confirm the logged
format before interpreting another surface format this way).
"""
import argparse
import json
import re
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    text = args.log.read_text(errors='replace')
    captures = {}

    def capture(number):
        return captures.setdefault(int(number), {'pixels': {}, 'rows': [], 'ended': False})

    for match in re.finditer(r'SWEET FB: copydump (\d+) ([^\r\n]+)', text):
        item = capture(match[1])
        if match[2] == 'end':
            item['ended'] = True
        else:
            item['geometry'] = match[2]
    words = r'([0-9a-fA-F]{8}(?: [0-9a-fA-F]{8}){7})'
    for match in re.finditer(r'SWEET FB: copyhex (\d+) (\d+),(\d+) ' + words, text):
        pixels = capture(match[1])['pixels']
        x, y = int(match[2]), int(match[3])
        for dx, word in enumerate(match[4].split()):
            pixels[(x + dx, y)] = int(word, 16)
    row_pattern = r'SWEET FB: copyrow (\d+) y (\d+) rgb (\d+) alpha (\d+) black (\d+) width (\d+)'
    for match in re.finditer(row_pattern, text):
        n, y, rgb, alpha, black, width = map(int, match.groups())
        capture(n)['rows'].append(dict(y=y, mean_rgb=rgb / (3 * width),
                                      mean_alpha=alpha / width, black_fraction=black / width))

    args.output.mkdir(parents=True, exist_ok=True)
    report = {}
    for number, item in sorted(captures.items()):
        pixels = item.pop('pixels')
        item['rectangles'] = []
        # Use the logged copy geometry so dropped edge packets cannot silently
        # shrink the expected rectangle and make incomplete data look complete.
        rect = re.search(r' rect (\d+),(\d+) (\d+)x(\d+)', item.get('geometry', ''))
        if rect:
            sx, sy, width, height = map(int, rect.groups())
            origins = [(sx, sy), (sx + (width - 64) // 2, sy + (height - 32) // 2)]
            for region, (x0, y0) in enumerate(origins):
                rgb = Image.new('RGB', (64, 32), (255, 0, 255))
                alpha = Image.new('L', (64, 32))
                observed = []
                for y in range(32):
                    for x in range(64):
                        word = pixels.get((x0 + x, y0 + y))
                        if word is None:
                            continue
                        colour = ((word >> 16) & 255, (word >> 8) & 255, word & 255)
                        rgb.putpixel((x, y), colour)
                        alpha.putpixel((x, y), word >> 24)
                        observed.append(word)
                stem = f'capture-{number}-region-{region}-{x0}-{y0}'
                rgb.save(args.output / f'{stem}-rgb.png')
                alpha.save(args.output / f'{stem}-alpha.png')
                item['rectangles'].append(dict(origin=[x0, y0], pixels=len(observed),
                    expected_pixels=2048, unique_words=len(set(observed)),
                    opaque_pixels=sum(v >> 24 == 255 for v in observed),
                    transparent_pixels=sum(v >> 24 == 0 for v in observed), stem=stem))
        else:
            item['error'] = 'Missing geometry header; raw pixel coverage cannot be established.'
        report[number] = item
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
