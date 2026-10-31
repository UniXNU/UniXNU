#!/usr/bin/env python3
"""Bind an offline display-query observation plan to unchanged target images."""
import hashlib
import argparse
import json
import mmap
from pathlib import Path
import re
import plistlib
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--discovery', action='store_true')
args = parser.parse_args()
cache = ROOT / '.cache/firmware/target-volumes/systemos-mount/System/Library/Caches/com.apple.dyld'
launchd = ROOT / '.cache/firmware/target-volumes/os-mount/sbin/launchd'
if hashlib.sha256(launchd.read_bytes()).hexdigest() != '8cec9a3c44a443b08e977ccc5d577850316ad428c575dc01f09b018dbd5b6a25':
    raise SystemExit('Require the unchanged supplied launchd')
if subprocess.check_output(['git', '-C', ROOT / 'refer/dyld', 'rev-parse', 'HEAD'], text=True).strip() != 'a571176e8e00c47e95b95e3156820ebec0cbd5e6':
    raise SystemExit('Require pinned dyld-1165.3 cache format')
work = ROOT / 'build/display-analysis'
work.mkdir(parents=True, exist_ok=True)
offsets = work / ('discovery-cache-offsets' if args.discovery else 'query-cache-offsets')
source = offsets.with_suffix('.cpp')
source.write_text('''#include <cstddef>
#include <cstdio>
#include "dyld_cache_format.h"
int main(){printf("%zu %zu %zu %zu %zu %zu %zu %zu %zu %zu\\n",
offsetof(dyld_cache_header,imagesTextOffset),offsetof(dyld_cache_header,localSymbolsOffset),
offsetof(dyld_cache_header,sharedRegionStart),sizeof(dyld_cache_image_text_info),
sizeof(dyld_cache_local_symbols_info),sizeof(dyld_cache_local_symbols_entry_64),
sizeof(dyld_cache_local_symbols_entry),offsetof(dyld_cache_header,symbolFileUUID),
offsetof(dyld_cache_header,mappingWithSlideOffset),sizeof(dyld_cache_mapping_and_slide_info));}
''')
subprocess.run(['xcrun', 'clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-I',
                ROOT / 'refer/dyld/cache-builder', source, '-o', offsets], check=True)
expected_offsets = [136, 72, 224, 32, 24, 16, 12, 400, 312, 56]
if list(map(int, subprocess.check_output([offsets], text=True).split())) != expected_offsets:
    raise SystemExit('Require the existing compiler-derived cache ABI qualification')
files, mappings, slide_mappings = [], [], []
for path in sorted(cache.glob('dyld_shared_cache_arm64*')):
    if path.suffix == '.symbols':
        continue
    stream = path.open('rb')
    data = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)
    files.append((path, stream, data))
    if data[:16].rstrip(b'\0') != b'dyld_v1   arm64':
        raise SystemExit('Require original ARM64 cache mappings')
    at, count = struct.unpack_from('<2I', data, 16)
    for i in range(count):
        va, size, off, _, prot = struct.unpack_from('<3Q2I', data, at + i * 32)
        mappings.append((va, va + size, off, data, path.name, prot))
    at, count = struct.unpack_from('<2I', data, 312)
    for i in range(count):
        va, size, _, off, length, _, _, _ = struct.unpack_from('<6Q2I', data, at + i * 56)
        if length and struct.unpack_from('<I', data, off)[0] == 2:
            mask, base = struct.unpack_from('<2Q', data, off + 24)
            slide_mappings.append((va, va + size, mask, base))


def read(va, size):
    for start, end, off, data, _, _ in mappings:
        if start <= va and va + size <= end:
            return data[off + va - start:off + va - start + size]
    raise SystemExit('Unbacked original cache address ' + hex(va))


def pointer(va):
    value, = struct.unpack('<Q', read(va, 8))
    for start, end, mask, base in slide_mappings:
        if start <= va < end:
            return (value & (~mask & ((1 << 64) - 1))) + base
    raise SystemExit('Require the original v2 slide pointer mapping')


def branch(pc):
    word, = struct.unpack('<I', read(pc, 4))
    if word & 0xfc000000 != 0x94000000:
        raise SystemExit('Expected original direct BL')
    offset = word & 0x3ffffff
    return pc + ((offset - (1 << 26) if offset & (1 << 25) else offset) << 2)


main = files[0][2]
textoff, count = struct.unpack_from('<2Q', main, 136)
images = {}
region, region_size, max_slide = struct.unpack_from('<3Q', main, 224)
for i in range(count):
    _, va, _, off = struct.unpack_from('<16sQ2I', main, textoff + i * 32)
    images[va - region] = main[off:main.find(b'\0', off)].decode()
query = 0x189549038
discovery = 0x1b63da630
expected_symbols = {query: b'__ZL14query_displaysv', discovery: b'___iomfb_populate_all_display_infos_block_invoke',
    0x1f4c4f698: b'_s_number_display_pipes', 0x1f4c4f6ac: b'_s_number_display_instances',
    0x1f4c500b8: b'_s_display_infos_len'}
with (cache / 'dyld_shared_cache_arm64.symbols').open('rb') as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as symbols:
    if symbols[88:104] != main[400:416]:
        raise SystemExit('Original local-symbol UUID must match main cache')
    lo, _ = struct.unpack_from('<2Q', symbols, 72)
    no, nc, so, ss, eo, ec = struct.unpack_from('<6I', symbols, lo)
    found = set()
    for i in range(ec):
        image, start, count = struct.unpack_from('<Q2I', symbols, lo + eo + i * 16)
        if images.get(image) not in ('/System/Library/Frameworks/QuartzCore.framework/QuartzCore',
                                    '/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer'):
            continue
        for j in range(start, start + count):
            name, kind, section, _, value = struct.unpack_from('<IBBHQ', symbols, lo + no + j * 16)
            if value in expected_symbols and kind & 0xe == 0xe and section and symbols[lo + so + name:symbols.find(b'\0', lo + so + name)] == expected_symbols[value]:
                found.add(value)
    if found != set(expected_symbols):
        raise SystemExit('Actual original QuartzCore local function identity differs')
fixups = subprocess.check_output(['xcrun', 'dyld_info', '-fixups', launchd], text=True)
slots = re.findall(r'__DATA_CONST\s+__got\s+(0x[0-9A-Fa-f]+)\s+bind\s+libSystem/___stack_chk_guard\s*$', fixups, re.M)
if slots != ['0x10006C0D0'] or pointer(0x1eb62bf98) != 0x1f4843c60:
    raise SystemExit('Original main guard binding and QuartzCore guard pointer must agree')


def uleb(data, at):
    value = shift = 0
    while True:
        byte = data[at]
        at += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, at
        shift += 7


libc = next(va + region for va, name in images.items() if name == '/usr/lib/system/libsystem_c.dylib')
_, _, _, _, count, size = struct.unpack('<6I', read(libc, 24))
commands = read(libc + 32, size)
at = 0
linkedit = export = None
for i in range(count):
    cmd, size = struct.unpack_from('<2I', commands, at)
    if cmd == 0x19 and commands[at + 8:at + 24].rstrip(b'\0') == b'__LINKEDIT':
        linkedit = struct.unpack_from('<4Q', commands, at + 24)
    if cmd == 0x80000033:
        export = struct.unpack_from('<2I', commands, at + 8)
    if cmd == 0x80000022 and struct.unpack_from('<I', commands, at + 44)[0]:
        export = struct.unpack_from('<2I', commands, at + 40)
    at += size
tree = read(linkedit[0] + export[0] - linkedit[2], export[1])
pending = [(0, '')]
guard = None
while pending:
    at, name = pending.pop()
    terminal, start = uleb(tree, at)
    if terminal and name == '___stack_chk_guard':
        flags, pos = uleb(tree, start)
        value, _ = uleb(tree, pos)
        if flags & 11:
            raise SystemExit('Require a regular, directly exported original stack guard')
        guard = libc + value
    at = start + terminal
    children = tree[at]
    at += 1
    for i in range(children):
        end = tree.index(0, at)
        label = tree[at:end].decode()
        child, at = uleb(tree, end + 1)
        pending.append((child, name + label))
if guard != 0x1f4843c60:
    raise SystemExit('Actual original libc guard export must qualify the slide anchor')
if branch(query + 0x34) != 0x18951d3ec or branch(query + 0x50) != 0x18954c428:
    raise SystemExit('Original query must call CARenderServerGetServerPort then CASGetDisplays')
if read(query + 0x38, 4) != bytes.fromhex('a01f0034') or read(0x18973b1c5, 25) != b'com.apple.CARenderServer\0':
    raise SystemExit('Original zero-port branch/bootstrap service identity differs')
request = struct.unpack('<2I', read(0x18970efa8, 8))[1]
if request != 40231:
    raise SystemExit('Original CASGetDisplays Mach request ID differs')
backboard = launchd.parents[1] / 'System/Library/LaunchDaemons/com.apple.backboardd.plist'
service = plistlib.loads(backboard.read_bytes())
if service['ProgramArguments'] != ['/usr/libexec/backboardd'] or service['MachServices']['com.apple.CARenderServer'] != {'ResetAtClose': True}:
    raise SystemExit('Original backboardd service declaration differs')
plan = dict(mode='query', expected_process='SpringBoard', launchd_sha256=hashlib.sha256(launchd.read_bytes()).hexdigest(),
    backboard_service_sha256=hashlib.sha256(backboard.read_bytes()).hexdigest(),
    cache_uuid=main[88:104].hex(), local_symbols_uuid=main[400:416].hex(),
    main_import_offset=int(slots[0], 16) - 0x100000000, unslid_import=0x1f4843c60,
    cache_region=region, cache_region_size=region_size, max_slide=max_slide,
    query=query, query_prefix=read(query, 16).hex(), port_checkpoint=0x38, reply_checkpoint=0x54, return_checkpoint=0x460,
    main_display=0x1f491b488, displays=0x1f491b498, cas_request_id=request,
    original_files_modified=False, static_only=True)
objects = ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837'
thread_object = objects / 'osfmk/DEVELOPMENT/thread.o'
proc_object = objects / 'bsd/DEVELOPMENT/kern_proc.o'


def member(obj, structure, name):
    text = subprocess.check_output(['xcrun', 'dwarfdump', '--name=' + structure, '--show-children', obj], text=True)
    match = re.search(r'DW_AT_name\s+\("' + name + r'"\)[\s\S]*?DW_AT_data_member_location\s+\((0x[0-9a-f]+)\)', text)
    if not match:
        raise SystemExit('Cannot derive compiler layout: ' + structure + '.' + name)
    return int(match[1], 16)


disassembly = subprocess.check_output(['xcrun', 'llvm-objdump', '--disassemble',
    '--disassemble-symbols=_proc_name_address', proc_object], text=True)
comm = re.search(r'add\s+x0, x0, #(0x[0-9a-f]+)', disassembly)
if not comm:
    raise SystemExit('Cannot derive actual process-name address from compiled accessor')
plan['process_layout'] = dict(thread_ro=member(thread_object, 'thread', 't_tro'),
    thread_user_state=member(thread_object, 'thread', 'machine')+member(thread_object, 'machine_thread', 'upcb'),
    ro_owner=member(thread_object, 'thread_ro', 'tro_owner'), ro_proc=member(thread_object, 'thread_ro', 'tro_proc'),
    pid=member(proc_object, 'proc', 'p_pid'), comm=int(comm[1], 16),
    thread_object_sha256=hashlib.sha256(thread_object.read_bytes()).hexdigest(),
    proc_object_sha256=hashlib.sha256(proc_object.read_bytes()).hexdigest())
task_object = objects / 'osfmk/DEVELOPMENT/task.o'
region_object = objects / 'osfmk/DEVELOPMENT/vm_shared_region.o'
plan['process_layout'].update(ro_task=member(thread_object, 'thread_ro', 'tro_task'),
    task_region=member(task_object, 'task', 'shared_region'), region_slide=member(region_object, 'vm_shared_region', 'sr_slide'),
    task_object_sha256=hashlib.sha256(task_object.read_bytes()).hexdigest(),
    region_object_sha256=hashlib.sha256(region_object.read_bytes()).hexdigest())
plan['thread_snapshot_layout'] = dict(
    proc_ro=member(proc_object, 'proc', 'p_proc_ro'),
    proc_ro_owner=member(proc_object, 'proc_ro', 'pr_proc'),
    proc_ro_task=member(proc_object, 'proc_ro', 'pr_task'),
    task_threads=member(task_object, 'task', 'threads'),
    task_thread_count=member(task_object, 'task', 'thread_count'),
    thread_link=member(thread_object, 'thread', 'task_threads'),
    thread_id=member(thread_object, 'thread', 'thread_id'),
    continuation=member(thread_object, 'thread', 'continuation'),
    wait_event=member(thread_object, 'thread', 'wait_event'),
    thread_state=member(thread_object, 'thread', 'state'),
    task_map=member(task_object, 'task', 'map'),
    map_pmap=member(task_object, '_vm_map', 'pmap'),
    pmap_ttep=member(objects / 'osfmk/DEVELOPMENT/pmap.o', 'pmap', 'ttep'),
    attr_root=member(objects / 'osfmk/DEVELOPMENT/pmap.o', 'page_table_attr', 'pta_root_level'),
    attr_shift=member(objects / 'osfmk/DEVELOPMENT/pmap.o', 'page_table_attr', 'pta_page_shift'))
plan['process_layout']['pmap_object_sha256'] = hashlib.sha256(
    (objects / 'osfmk/DEVELOPMENT/pmap.o').read_bytes()).hexdigest()
native_path = objects / 'mach.development.bcm2837.unstripped'
native_symbols = subprocess.check_output(['xcrun', 'nm', '-U', native_path], text=True)
if '"pmap_pt_attr"' in subprocess.check_output(['xcrun', 'dwarfdump', '--name=pmap', '--show-children',
        objects / 'osfmk/DEVELOPMENT/pmap.o'], text=True):
    raise SystemExit('Thread stack observer requires the qualified non-parameterized pmap build')
plan['thread_snapshot_native_pt_attr'] = int(re.search(
    r'^([0-9a-f]+)\s+\S\s+_native_pt_attr$', native_symbols, re.M)[1], 16)
plan['native_sha256'] = hashlib.sha256(native_path.read_bytes()).hexdigest()
plan['process_activation'] = []
for name in ('_shared_region_check_np', '_shared_region_map_and_slide_2_np'):
    match = re.search(r'^([0-9a-f]+)\s+\S\s+' + name + '$', native_symbols, re.M)
    if not match:
        raise SystemExit('Cannot resolve actual shared-region activation function')
    plan['process_activation'].append(int(match[1], 16))
if args.discovery:
    if branch(discovery + 0x64) != 0x1ba64c6c8 or read(0x1b63dd589, len(b'IODeviceTree:/arm-io\0')) != b'IODeviceTree:/arm-io\0':
        raise SystemExit('Original discovery must look up its actual arm-io registry path')
    plan.update(mode='discovery', expected_process='backboardd', query=discovery, query_prefix=read(discovery, 16).hex(), port_checkpoint=0x68,
                reference_count=0x1f4c4f698, enumerated_count=0x1f4c4f6ac, display_count=0x1f4c500b8, return_checkpoint=0x484)
if read(plan['query'] + plan['return_checkpoint'], 4) != bytes.fromhex('c0035fd6'):
    raise SystemExit('Require the original function epilogue RET checkpoint')
output = work / ('discovery-plan.json' if args.discovery else 'query-plan.json')
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(plan, indent=2) + '\n')
print('PASS: unchanged original launchd binding, UUID-bound QuartzCore query, server call chain and CASGetDisplays request', request)
