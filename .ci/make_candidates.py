#!/usr/bin/env python3
"""Produce the prelink candidates the driver archives audit against.

The public repositories ship the audit scripts but not the build/native-prelink
candidates they read; those are working artefacts of the original port. Once a kernel
links, the candidates can be regenerated here: prelink the linked kernel with the
original kernelcache exactly the way unixnu's own prelink step does, then publish the
result under every name the archives expect.
"""
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path.cwd()
TREE = REPO / 'out/sheng/tree'
BOARD = REPO / 'device/board.toml'

NAMES = (
    'native-owner-ufs-rootauth3-candidate',
    'native-owner-mobile-graphics-candidate',
    'native-apfs-load-positive',
    'native-owner-ufs-cpu-desktop-bootstrap-candidate',
)


def main():
    spec = tomllib.loads(BOARD.read_text())['kernel']['prelink']
    kernel = TREE / spec['kernel']
    if not kernel.is_file():
        print(f'linked kernel missing: {kernel}')
        return 1

    caches = sorted((REPO / 'out/ipsw').glob('*/kernelcache.decompressed'))
    if not caches:
        print('no decompressed kernelcache under out/ipsw')
        return 1
    cache = caches[0]
    print(f'kernel: {kernel}\nkernelcache: {cache}')

    out_dir = TREE / 'build/native-prelink'
    out_dir.mkdir(parents=True, exist_ok=True)
    first = out_dir / f'{NAMES[0]}.macho'
    for stale in (first, first.with_suffix('.json')):
        stale.unlink(missing_ok=True)

    command = [sys.executable, str(TREE / spec['tool']), '--kernel', str(kernel),
               '--prelinked', str(cache), f'--slide={spec["slide"]}', '--output', str(first)]
    for root in spec.get('roots', []):
        command += ['--root', root]
    if spec.get('early_security_init'):
        command += ['--early-security-init', spec['early_security_init']]
    result = subprocess.run(command, cwd=TREE, capture_output=True, text=True)
    print(result.stdout[-1500:])
    print(result.stderr[-1500:], file=sys.stderr)
    if result.returncode or not first.is_file():
        print(f'emit_prelink failed ({result.returncode})')
        return 1

    plan = first.with_suffix('.json')
    for name in NAMES[1:]:
        shutil.copyfile(first, out_dir / f'{name}.macho')
        shutil.copyfile(plan, out_dir / f'{name}.json')
    for path in sorted(out_dir.glob('*')):
        print(f'  {path.name} {path.stat().st_size} bytes')
    print(json.dumps({'candidate': first.name, 'candidate_sha256': json.loads(plan.read_text())['candidate_sha256']}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
