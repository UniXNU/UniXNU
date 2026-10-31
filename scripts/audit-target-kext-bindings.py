#!/usr/bin/env python3
"""Audit exact prelink slide sites against a source-built kernel, without loading.

The upstream KASLR list identifies absolute pointers, not original link symbols
or a complete relocation recipe. PC-relative references and ABI compatibility
remain separate requirements. No target bytes or signatures are changed.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bundle', default='com.apple.driver.AppleMobileFileIntegrity')
args = parser.parse_args()
folder = ROOT / 'build/target-kexts' / args.bundle
metadata = json.loads((folder / 'segments.json').read_text())
stock = ROOT / '.cache/firmware/kernelcache.macho/kernelcache.release.ipad7.decompressed'
baseline = ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped'
data = stock.read_bytes()
if hashlib.sha256(data).hexdigest() != 'f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7':
    raise SystemExit('Wrong target kernelcache')


def segments(at):
    magic, cpu, subtype, _, count, size = struct.unpack_from('<6I', data, at)
    if (magic, cpu, subtype) != (0xfeedfacf, 0x100000c, 0):
        raise ValueError('Expected supplied ordinary ARM64 Mach-O')
    offset = at + 32
    result = []
    for _ in range(count):
        command, length = struct.unpack_from('<II', data, offset)
        if length < 8 or offset + length > at + 32 + size or at + 32 + size > len(data):
            raise ValueError(f'Malformed load command extent at {at:#x}: command={command:#x}, offset={offset:#x}, length={length:#x}, count={count}, size={size:#x}')
        if command == 0x19:
            name, va, vmsize, fileoff, filesize = struct.unpack_from('<16s4Q', data, offset + 8)
            result.append({'name': name.rstrip(b'\0').decode(), 'va': va, 'size': vmsize,
                           'fileoff': fileoff, 'filesize': filesize})
        offset += length
    if offset != at + 32 + size:
        raise ValueError('Load command size mismatch')
    return result


parent = segments(0)


def file_offset(va, length):
    matches = [s['fileoff'] + va - s['va'] for s in parent
               if s['va'] <= va and va + length <= s['va'] + s['filesize']]
    if len(matches) != 1 or matches[0] + length > len(data):
        raise ValueError(f'Ambiguous/unbacked cache extent {va:#x}+{length:#x}')
    return matches[0]


owners = []
interface_records = []
for entry in json.loads((ROOT / 'build/target-kexts/inventory.json').read_text()):
    if entry['CFBundleIdentifier'].startswith('com.apple.kpi.'):
        # These packed KPI symbol-set records contain no executable mappings.
        interface_records.append(entry['CFBundleIdentifier'])
        continue
    va = entry.get('_PrelinkExecutableLoadAddr')
    if va is None or not entry.get('_PrelinkExecutableSize'):
        continue
    try:
        module_segments = segments(file_offset(va, 32))
    except ValueError as error:
        raise ValueError(f'{entry["CFBundleIdentifier"]}: {error}') from error
    for segment in module_segments:
        if segment['size'] and segment['name'] != '__LINKEDIT':
            owners.append((segment, entry['CFBundleIdentifier']))


def ownership(va):
    return sorted({name for s, name in owners if s['va'] <= va < s['va'] + s['size']})


def symbols(path):
    result = {}
    for line in subprocess.check_output(['xcrun', 'nm', '-g', '-n', path], text=True).splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1].upper() != 'U':
            result.setdefault(int(parts[0], 16), []).append(parts[2])
    return result


old_symbols = symbols(stock)
new_symbols = {}
for address, names in symbols(baseline).items():
    for name in names:
        new_symbols.setdefault(name, set()).add(address)
relocations = (ROOT / 'build/target-kexts/prelink-kaslr.bin').read_bytes()
count, = struct.unpack_from('<I', relocations)
if len(relocations) != 4 + count * 4:
    raise SystemExit('Malformed exact KASLR pointer table')
offsets = struct.unpack_from(f'<{count}I', relocations, 4)
if len(set(offsets)) != count:
    raise SystemExit('Duplicate exact KASLR sites')
base = next(s['va'] for s in parent if s['name'] == '__PRELINK_TEXT')
records = []
for offset in offsets:
    site = base + offset
    if not any(s['va'] <= site < s['va'] + s['size'] for s in metadata['segments']):
        continue
    if ownership(site) != [args.bundle] or ownership(site + 7) != [args.bundle]:
        raise SystemExit(f'Overlapping module ownership at {site:#x}')
    target, = struct.unpack_from('<Q', data, file_offset(site, 8))
    target_owners = ownership(target)
    names = old_symbols.get(target, [])
    candidates = sorted({address for name in names for address in new_symbols.get(name, set())})
    if target_owners == [args.bundle]:
        kind = 'internal-pointer'
    elif target_owners:
        kind = 'cross-kext-pointer'
    elif len(candidates) == 1:
        kind = 'kernel-symbol-candidate'
    elif candidates:
        kind = 'ambiguous-kernel-symbol'
    elif names:
        kind = 'missing-kernel-symbol'
    else:
        kind = 'unresolved-external-pointer'
    records.append({'site': hex(site), 'target': hex(target), 'kind': kind,
                    'target_owners': target_owners, 'stock_export_names': names,
                    'baseline_address_candidates': [hex(value) for value in candidates]})
def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


# Encoding inventory, not control-flow recovery: executable ranges may include
# literal data. An ADRP page match alone does not resolve its later consumers.
pc_relative = []
for segment in metadata['segments']:
    if segment['name'] != '__TEXT_EXEC':
        continue
    blob = (folder / '__TEXT_EXEC.bin').read_bytes()
    if hashlib.sha256(blob).hexdigest() != segment['sha256']:
        raise SystemExit('Extracted executable segment digest mismatch')
    for offset in range(0, len(blob) - 3, 4):
        word, = struct.unpack_from('<I', blob, offset)
        pc = segment['va'] + offset
        if word & 0x9f000000 in (0x10000000, 0x90000000):
            immediate = signed(((word >> 5) & 0x7ffff) << 2 | ((word >> 29) & 3), 21)
            page = bool(word & 0x80000000)
            target = (pc & ~4095) + (immediate << 12) if page else pc + immediate
            kind = 'adrp-page' if page else 'adr'
        elif word & 0x7c000000 == 0x14000000:
            target = pc + (signed(word & 0x3ffffff, 26) << 2)
            kind = 'b-or-bl'
        elif word & 0xff000010 == 0x54000000:
            target = pc + (signed((word >> 5) & 0x7ffff, 19) << 2)
            kind = 'conditional-branch'
        elif word & 0x7e000000 == 0x34000000:
            target = pc + (signed((word >> 5) & 0x7ffff, 19) << 2)
            kind = 'compare-branch'
        elif word & 0x7e000000 == 0x36000000:
            target = pc + (signed((word >> 5) & 0x3fff, 14) << 2)
            kind = 'test-bit-branch'
        elif word & 0x3b000000 == 0x18000000:
            target = pc + (signed((word >> 5) & 0x7ffff, 19) << 2)
            kind = 'literal-load-or-prefetch'
        else:
            continue
        if kind == 'adrp-page':
            internal = any((s['va'] & ~4095) <= target < ((s['va'] + s['size'] + 4095) & ~4095)
                           for s in metadata['segments'])
        else:
            internal = any(s['va'] <= target < s['va'] + s['size'] for s in metadata['segments'])
        pc_relative.append({'site': hex(pc), 'target': hex(target), 'kind': kind,
                            'within_module_extent_or_adrp_page': internal})


summary = dict(Counter(record['kind'] for record in records))
report = {'bundle_id': args.bundle, 'stock_sha256': hashlib.sha256(data).hexdigest(),
          'baseline_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
          'kaslr_table_sha256': hashlib.sha256(relocations).hexdigest(),
          'excluded_kernel_kpi_symbol_sets': interface_records,
          'total_cache_pointer_sites': count, 'module_pointer_sites': len(records),
          'summary': summary, 'pointers': records,
          'pc_relative_encoding_counts': dict(Counter(record['kind'] for record in pc_relative)),
          'pc_relative_encodings_outside_module': [r for r in pc_relative if not r['within_module_extent_or_adrp_page']],
          'pc_relative_consumer_dataflow_proven': False,
          'complete_relocation_recipe': False, 'abi_compatibility_proven': False,
          'pc_relative_references_audited': False, 'target_bytes_modified': False}
(folder / 'exact-pointer-audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ('bundle_id', 'module_pointer_sites', 'summary')}, indent=2))
print('PC-relative encoding counts:', report['pc_relative_encoding_counts'])
print('Encodings outside module extents/pages:', len(report['pc_relative_encodings_outside_module']))
print('Static pointer inventory only: no module loaded, no ABI/PC-relative binding proof')
