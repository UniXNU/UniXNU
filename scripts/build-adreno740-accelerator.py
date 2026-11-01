#!/usr/bin/env python3
"""Build the staged AGXAccelerator class (drivers/Adreno740/NativeAdrenoAccelerator.cpp) against the audited original
IOAcceleratorES imports, as a "late" archive: its static initializer is removed from __mod_init_func and exported so the board
probe runs it after the original IOGPUFamily kext has loaded. Same binding recipe as build-native-accelerator-abi.py (exact
original constructor, destructor and metaclass addresses from build/gpu-analysis/ioaccelerator-base-abi.json)."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/adreno740-accelerator'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / 'kits/XnuPrelink'))
from native_prelink import macho as ordinary_macho


def macho(data):
    # The layout of an arm64e object is that of arm64; only the CPU subtype (2, with the pointer-authentication ABI flags) differs.
    if len(data) >= 12 and struct.unpack_from('<I', data, 8)[0] & 0xff == 2:
        data = data[:8] + bytes(4) + data[12:]
    return ordinary_macho(data)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from kernel_target import ARCH, IOS_VERSION, TRIPLE


def run(cmd, **kw):
    return subprocess.check_output([str(x) for x in cmd], timeout=120, **kw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# iPadOS 27 (arm64e fileset): the reviewed 24A446 plan, original addresses before the collection slide.
FILESET = ARCH == 'arm64e' and IOS_VERSION.split('.')[0] == '27'
plan_path = ROOT / ('build/gpu-analysis/ioaccelerator-base-abi-24A446.json' if FILESET else 'build/gpu-analysis/ioaccelerator-base-abi.json')
# The audit of the original base class needs the hardware-observed parent evidence of the audited kernel; its recorded result
# ships with the scripts and seeds a fresh tree.
recorded = ROOT / ('scripts/data/ioaccelerator-base-abi-24A446.json' if FILESET else 'scripts/data/ioaccelerator-base-abi.json')
if not plan_path.exists() and recorded.exists():
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_bytes(recorded.read_bytes())
if not plan_path.exists():
    print(run(['python3', ROOT / 'scripts/audit-target-accelerator-base.py'], text=True), end='')
plan = json.loads(plan_path.read_text())
if plan['operational_overrides'] or plan['instance_bytes'] != 136 or plan['virtual_entries'] != 168:
    sys.exit('The audited original base is not the expected 136-byte, 168-entry class without operational overrides')

record = json.loads((ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json').read_text().strip().rstrip(','))
source = ROOT / 'drivers/Adreno740/NativeAdrenoAccelerator.cpp'
obj = OUT / 'NativeAdrenoAccelerator.o'
cmd, i, args = [], 0, record['arguments']
while i < len(args):
    v = args[i]
    if v == record['file']:
        cmd.append(str(source))
    elif v == '-o':
        cmd += ['-o', str(obj)]
        i += 1
    elif v == '-Xclang' and args[i + 1].startswith('-W'):
        i += 1
    elif not v.startswith('-W') and v not in ('-MD', '-MP'):
        cmd.append(v)
    i += 1
    if v in ('-MF', '-MJ'):
        i += 1
cmd += ['-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-Wno-unnecessary-virtual-specifier', '-Wno-c99-designator',
        '-Wno-reorder-init-list', '-Wno-deprecated-enum-enum-conversion', '-Wno-overloaded-virtual',
        '-I', str(ROOT / '.cache/xnu-work/osfmk')]
subprocess.run(cmd, cwd=record['directory'], check=True)

raw = obj.read_bytes()
im = macho(raw)
st = next(p for c, p, _ in im['commands'] if c == 2)
at, count, strings, _ = struct.unpack_from('<4I', raw, st + 8)
symbols = []
for k in range(count):
    ix, kind, section, _, va = struct.unpack_from('<IBBHQ', raw, at + k * 16)
    symbols.append((raw[strings + ix:raw.index(b'\0', strings + ix)].decode(), va, kind))
bindings = {'__ZN15IOAcceleratorESC2EPK11OSMetaClass': int(plan['protected_compatible_constructor_aliases'][0], 16),
            '__ZN15IOAcceleratorESD2Ev': int(plan['nondeleting_destructor'], 16),
            '__ZN15IOAcceleratorES10gMetaClassE': int(plan['metaclass'], 16)}
undefined = {n for n, _, k in symbols if k == 1 and 'IOAcceleratorES' in n}
extra = undefined - set(bindings)
if extra or not undefined & set(bindings):
    sys.exit('Unexpected original-base imports: %s' % sorted(extra))
asm = OUT / 'original-bindings.S'
sdk = run(['xcrun', '--sdk', 'iphoneos', '--show-sdk-path'], text=True).strip()
binding_objects = [OUT / 'original-bindings.o']
if FILESET:
    # As for the Legacy display (build-gop-legacy-display-27.py): original functions are reached through owned stubs in kernel text
    # (signed and moved like native code) whose branch lands on the original after the collection slide, less the measured move of the
    # native kernel (native-slide); the metaclass is data, reached through the GOT at its plain address.
    slide = int(plan['collection_slide'], 16)
    native_slide_file = ROOT / 'build/native-legacy-display/native-slide'
    native_slide = int(native_slide_file.read_text(), 16) if native_slide_file.exists() else 0
    text, addresses = '.text\n.p2align 2\n', ''
    for n, a in sorted(bindings.items()):
        if n not in undefined:
            continue
        if n.endswith('gMetaClassE'):
            addresses += f'.globl {n}\n.set {n}, {a + slide:#x}\n'
        else:
            addresses += f'.globl {n}.original\n.set {n}.original, {(a + slide - native_slide) & ((1 << 64) - 1):#x}\n'
            text += f'.globl {n}\n{n}:\n bti c\n b {n}.original\n'
    asm.write_text(text)
    (OUT / 'original-addresses.S').write_text(addresses)
    run(['xcrun', 'clang', '-target', TRIPLE, '-isysroot', sdk, '-c', OUT / 'original-addresses.S', '-o', OUT / 'original-addresses.o'])
    binding_objects.append(OUT / 'original-addresses.o')
else:
    asm.write_text(''.join(f'.globl {n}\n.set {n}, {a:#x}\n' for n, a in sorted(bindings.items()) if n in undefined))
run(['xcrun', 'clang', '-target', TRIPLE, '-isysroot', sdk, '-c', asm, '-o', OUT / 'original-bindings.o'])

llvm = Path(run(['brew', '--prefix', 'llvm'], text=True).strip()) / 'bin'
late = OUT / 'NativeAdrenoAccelerator.late.o'
run([llvm / 'llvm-objcopy', '--remove-section=__DATA,__mod_init_func',
     '--globalize-symbol=__GLOBAL__sub_I_NativeAdrenoAccelerator.cpp', obj, late])


def code(p):
    b = p.read_bytes()
    s = next(s for g in macho(b)['segments'] for s in g['sections'] if s['name'] == '__text')
    return b[s['fileoff']:s['fileoff'] + s['size']]


if code(obj) != code(late):
    sys.exit('Only the owned initializer registration may change')
archive = OUT / 'libAdreno740Accelerator.late.a'
archive.unlink(missing_ok=True)
run(['xcrun', 'ar', 'rcs', archive, late, *binding_objects])
# The kernel links libAdreno740.a; the staged class rides in it (its initializer is not in __mod_init_func).
native = ROOT / 'build/adreno740/libAdreno740.a'
if native.exists():
    run(['xcrun', 'ar', 'rcs', native, late, *binding_objects])
(OUT / 'build-report.json').write_text(json.dumps(dict(
    # The header the source includes (#include "../AdrenoMetal/OriginalAcceleratorABI.h", beside the driver's own checkout).
    source_sha256={str(source.relative_to(ROOT)): sha(source),
                   'OriginalAcceleratorABI.h': sha(source.resolve().parent.parent / 'AdrenoMetal/OriginalAcceleratorABI.h')},
    archive_sha256=sha(archive), original_abi_sha256=sha(plan_path), bindings={n: hex(a) for n, a in bindings.items()},
    original_instructions_modified=False, runtime_qualified=False), indent=2) + '\n')
print('PASS: staged AGXAccelerator builds against the audited original IOAcceleratorES imports')
