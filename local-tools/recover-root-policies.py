#!/usr/bin/env python3
"""Recover root policy headers and their owner anchor from a built payload.

Usage: recover-root-policies.py PAYLOAD_FAT POLICIES --verification-from DIR [--write]

DIR supplies each window's verification.json. Headers must match image_sha256 and
its owner anchor must match trusted_key_sha256. Use --write to restore the matching
files under POLICIES. Requires mtools.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

WINDOWS = ('OS', 'SystemOS', 'App')
KEY_BYTES, HEADER_BYTES = 395, 544


def mcopy(fat, name, out):
    subprocess.run(['mcopy', '-n', '-i', str(fat), f'::/EFI/UniXNU/Payloads/{name}', str(out)], check=True)
    return out.read_bytes()


def headers(bundle):
    magic, version, count, total = struct.unpack_from('<8sQQQ', bundle, 0)
    if magic != b'VROOTB01' or version != 1 or total != len(bundle):
        raise SystemExit('kernel.macho.vroot is not a VROOTB01 bundle of this format')
    out = []
    for i in range(count):
        offset, length = struct.unpack_from('<QQ', bundle, 32 + 16 * i)
        out.append(bundle[offset:offset + length])
    return out


def find_key(kernel, wanted):
    # Scan fixed-length candidates for the recorded anchor digest.
    hits = []
    for start in range(len(kernel) - KEY_BYTES + 1):
        if hashlib.sha256(kernel[start:start + KEY_BYTES]).hexdigest() == wanted:
            hits.append(start)
            break
    return hits


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('payload')
    parser.add_argument('policies', type=Path)
    parser.add_argument('--verification-from', type=Path, required=True)
    parser.add_argument('--key-hint', help='hex prefix the anchor starts with, to narrow the scan')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    records = {w: json.loads((args.verification_from / w / 'verification.json').read_text()) for w in WINDOWS
               if (args.verification_from / w / 'verification.json').is_file()}
    keys = {r['trusted_key_sha256'] for r in records.values()}
    if len(keys) != 1:
        raise SystemExit(f'the windows name {len(keys)} different anchors')
    wanted = keys.pop()
    with tempfile.TemporaryDirectory() as scratch:
        bundle = mcopy(args.payload, 'kernel.macho.vroot', Path(scratch) / 'vroot')
        kernel = mcopy(args.payload, 'kernel.macho', Path(scratch) / 'kernel')
    found = {}
    for data in headers(bundle):
        for window, record in records.items():
            if len(data) == HEADER_BYTES and data[56:88].hex() == record['image_sha256']:
                found[window] = data
    missing = [w for w in records if w not in found]
    if missing:
        raise SystemExit(f'no header in the bundle describes {", ".join(missing)}')
    start = -1
    if args.key_hint:
        prefix = bytes.fromhex(args.key_hint)
        at = kernel.find(prefix)
        while at >= 0:
            if hashlib.sha256(kernel[at:at + KEY_BYTES]).hexdigest() == wanted:
                start = at
                break
            at = kernel.find(prefix, at + 1)
    if start < 0:
        hits = find_key(kernel, wanted)
        start = hits[0] if hits else -1
    if start < 0:
        raise SystemExit('the anchor the policies name is not in kernel.macho')
    key = kernel[start:start + KEY_BYTES]
    print(f'anchor at kernel offset {start:#x}, sha256 {wanted[:12]}...; headers for {", ".join(found)}')
    for window, data in found.items():
        target = args.policies / window
        print(f'{target}: manifest.header.bin {hashlib.sha256(data).hexdigest()[:12]}, trusted-key.bin {wanted[:12]}'
              + ('' if args.write else ' (not written)'))
        if args.write:
            target.mkdir(parents=True, exist_ok=True)
            (target / 'manifest.header.bin').write_bytes(data)
            (target / 'trusted-key.bin').write_bytes(key)
    return 0


if __name__ == '__main__':
    sys.exit(main())
