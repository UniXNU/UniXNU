#!/usr/bin/env python3
"""Compare visible prelinked corecrypto branch/pointer edges with baseline KPIs.

This is a partial static survey. It cannot recover stripped relocations,
prove ABI compatibility, or make the extracted bytes loadable.
"""
import argparse
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
stock = ROOT / '.cache/firmware/kernelcache.macho/kernelcache.release.ipad7.decompressed'
baseline = ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bundle', default='com.apple.kec.corecrypto')
args = parser.parse_args()
folder = ROOT / 'build/target-kexts' / args.bundle
metadata = json.loads((folder / 'segments.json').read_text())


def symbols(path):
    result = {}
    output = subprocess.check_output(['xcrun', 'nm', '-g', '-n', str(path)], text=True)
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1].upper() != 'U':
            result.setdefault(int(parts[0], 16), []).append(parts[2])
    return result


old_symbols = symbols(stock)
new_symbols = {name for names in symbols(baseline).values() for name in names}
segments = metadata['segments']


def owned(address):
    return any(segment['va'] <= address < segment['va'] + segment['size'] for segment in segments)


edges = []
unresolved_branches = []
for segment in segments:
    data = (folder / f'{segment["name"]}.bin').read_bytes()
    if segment['name'] == '__TEXT_EXEC':
        for offset in range(0, len(data) - 3, 4):
            instruction = struct.unpack_from('<I', data, offset)[0]
            if instruction & 0x7c000000 != 0x14000000:
                continue
            immediate = instruction & 0x3ffffff
            if immediate & 0x2000000:
                immediate -= 0x4000000
            target = segment['va'] + offset + immediate * 4
            if owned(target):
                continue
            names = old_symbols.get(target, [])
            edge = {'site': hex(segment['va'] + offset), 'target': hex(target),
                    'kind': 'direct-branch', 'stock_symbols': names,
                    'baseline_symbols': [name for name in names if name in new_symbols]}
            edges.append(edge)
            if not names:
                unresolved_branches.append(edge)
    elif segment['name'] in ('__DATA', '__DATA_CONST'):
        for offset in range(0, len(data) - 7, 8):
            target = struct.unpack_from('<Q', data, offset)[0]
            if target in old_symbols and not owned(target):
                names = old_symbols[target]
                edges.append({'site': hex(segment['va'] + offset), 'target': hex(target),
                              'kind': 'aligned-pointer', 'stock_symbols': names,
                              'baseline_symbols': [name for name in names if name in new_symbols]})
names = sorted({name for edge in edges for name in edge['stock_symbols']})
report = {'edges': edges, 'visible_symbols': names,
          'missing_baseline_names': [name for name in names if name not in new_symbols],
          'unresolved_direct_branches': unresolved_branches,
          'complete_import_inventory': False, 'abi_compatibility_proven': False,
          'stripped_relocation_tables': True}
(folder / 'edge-survey.json').write_text(json.dumps(report, indent=2) + '\n')
print(f'{len(edges)} visible edges, {len(names)} symbol names, {len(unresolved_branches)} unnamed branches')
print('Names absent from baseline:', report['missing_baseline_names'])
