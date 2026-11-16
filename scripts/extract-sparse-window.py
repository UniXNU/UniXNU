#!/usr/bin/env python3
"""Extract a byte window from an Android sparse backup for read-only mounting."""
import argparse
import os
from pathlib import Path
import shutil
import struct
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--offset', type=lambda s: int(s, 0), required=True)
    parser.add_argument('--bytes', type=lambda s: int(s, 0), required=True)
    args = parser.parse_args()
    if args.output.exists() or args.offset < 0 or args.bytes <= 0:
        parser.error('require a new output path and a positive window')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(args.output.parent).free < args.bytes + (1 << 30):
        parser.error('the window requires its full size plus 1 GiB free space')
    start, end = args.offset, args.offset + args.bytes
    with args.source.open('rb') as source, tempfile.NamedTemporaryFile(
            prefix=args.output.name + '.', dir=args.output.parent, delete=False) as output:
        try:
            magic, major, _, header, chunk_header, block, blocks, chunks, _ = struct.unpack('<I4H4I', source.read(28))
            if magic != 0xed26ff3a or major != 1 or header < 28 or chunk_header < 12 or end > block * blocks:
                parser.error('invalid Android sparse image or window')
            source.seek(header)
            logical = 0
            for _ in range(chunks):
                chunk_at = source.tell()
                kind, _, count, total = struct.unpack('<2H2I', source.read(12))
                size = count * block
                if total < chunk_header:
                    parser.error('invalid sparse chunk length')
                lo, hi = max(start, logical), min(end, logical + size)
                if lo < hi:
                    length = hi - lo
                    output.seek(lo - start)
                    source.seek(chunk_at + chunk_header)
                    if kind == 0xcac1:
                        if total - chunk_header != size:
                            parser.error('invalid raw chunk length')
                        source.seek(lo - logical, 1)
                        remaining = length
                        while remaining:
                            data = source.read(min(remaining, 8 << 20))
                            if not data:
                                parser.error('truncated raw chunk')
                            output.write(data)
                            remaining -= len(data)
                    elif kind == 0xcac2:
                        fill = source.read(4)
                        if len(fill) != 4 or total - chunk_header != 4:
                            parser.error('invalid fill chunk')
                        if fill != bytes(4):
                            shift = (lo - logical) % 4
                            fill = (fill * 2)[shift:shift + 4]
                            data = fill * (2 << 20)
                            while length:
                                piece = data[:min(length, len(data))]
                                output.write(piece)
                                length -= len(piece)
                    elif kind != 0xcac3:
                        parser.error(f'unsupported sparse chunk {kind:#x}')
                logical += size
                source.seek(chunk_at + total)
            if logical != block * blocks:
                parser.error('sparse chunks do not cover the declared image')
            output.truncate(args.bytes)
            output.flush()
            os.replace(output.name, args.output)
        finally:
            Path(output.name).unlink(missing_ok=True)
    print(f'{args.output}: extracted {args.bytes} bytes at {args.offset}')


if __name__ == '__main__':
    main()
