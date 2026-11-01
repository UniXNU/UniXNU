#!/usr/bin/env python3
"""Build a symbol-bearing RELEASE comparison kernel in an isolated output tree."""
import json
import os
import shutil
import hashlib
import argparse
import fnmatch
from pathlib import Path
import subprocess

repo = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tree', required=True, type=Path, help='prepared XNU build tree of the OS profile')
parser.add_argument('--lto', action='store_true', help='enable the RELEASE default link-time optimization')
options = parser.parse_args()
mode = 'lto' if options.lto else 'snapshot'
root = options.tree.resolve()
output = root / 'build/xnu/fileset-reference'
final = output / 'mach.release.bcm2837.unstripped.noctf'
if final.is_file():
    # An earlier run of this step left the comparison kernel in place.
    print(f'reference present: {final}')
    raise SystemExit(0)
output.mkdir(parents=True, exist_ok=True)
source = output / 'source'
if not source.exists():
    shutil.copytree(root/'.cache/xnu-work', source, symlinks=True,
                    ignore=shutil.ignore_patterns('.git'))
    # The shared tree currently has this observation hook at file scope. The
    # reference build disables observation hooks; repair only its private copy.
    sleh = source / 'osfmk/arm64/sleh.c'
    text = sleh.read_text()
    misplaced = '\n\tboot_progress_user_breakpoint(state, esr);\n#if __has_feature(ptrauth_calls)'
    if misplaced in text:
        sleh.write_text(text.replace(misplaced, '\n#if __has_feature(ptrauth_calls)', 1))
    manifest = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source.rglob('*') if p.is_file()}
    (output/'source-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
sdk = root / '.cache/fakeroot'
archives = [root/'build/corecrypto-2023/libcorecrypto_kernel_noasm-namespaced.a']
forced = [root/f'build/{folder}/{name}' for folder,name in (
    ('libpthread-kernel','libpthread_kernel.a'),('armdt-platform','libArmDTPlatform.a'),('armcpu','libArmCpu.a'))]
assert all(p.is_file() for p in archives+forced)
env = dict(os.environ, KERNEL_SDKROOT=str(sdk),
           XNU_AVAILABILITY_PL=str(sdk/'usr/local/libexec/availability.pl'))
flags = '-Wno-reserved-identifier -Wno-pre-c11-compat -Wno-missing-designated-field-initializers -Wno-suggest-override -Wno-unnecessary-virtual-specifier -Wno-suggest-destructor-override -Wno-ms-bitfield-padding -DXNU_NATIVE_PAN=1 -DXNU_SOURCE_CORECRYPTO14=1 -DXNU_BOOT_PROGRESS=0'
args = ['make','-C',str(source),'build','SDKROOT=iphoneos',
    'ARCH_CONFIGS=ARM64','MACHINE_CONFIGS=BCM2837','KERNEL_CONFIGS=RELEASE',
    'ARCH_STRING_FOR_CURRENT_MACHINE_CONFIG=arm64e','LARGE_MEMORY_DEFINE=-UARM_LARGE_MEMORY',
    'ARM64_LINK_ADDR=0xfffffff007004000','ARM64_PLKSEG_ADDR=0xfffffff004004000',
    f'DEPLOYMENT_TARGET_FLAGS=-miphoneos-version-min={os.environ.get("UNIXNU_IOS_VERSION", "26.0")} -DXNU_TARGET_OS_IOS',
    f'DEPLOYMENT_LINKER_FLAGS=-Wl,-ios_version_min,{os.environ.get("UNIXNU_IOS_VERSION", "26.0")}',
    f'RC_DARWIN_KERNEL_VERSION={os.environ.get("UNIXNU_XNU_DARWIN", "25.5.0")}',
    f'RC_ProjectSourceVersion={os.environ.get("UNIXNU_XNU_VERSION", "12377.121.6")}',
    f'BUILD_LTO={int(options.lto)}','BOUND_CHECKS=0','BUILD_WERROR=0','MAKEJOBS=-j8',
    'LDFLAGS_KERNEL_LTO=-miphoneos-version-min=26.0 -Wl,-mllvm,-inline-threshold=100',
    f'CFLAGS_EXTRA={flags}',
    'copyio.o_CFLAGS_ADD=-march=armv8.1-a','pcb.o_CFLAGS_ADD=-march=armv8.1-a',
    'LD_KERNEL_ARCHIVES='+' '.join([f'-L{sdk}/usr/local/lib/kernel','-lfirehose_kernel',
                                    *map(str,archives),*(f'-Wl,-force_load,{p}' for p in forced)]),
    'XNU_EXTERNAL_KERNEL_ARCHIVES='+' '.join(map(str,archives+forced)),
    f'OBJROOT={output}/{mode}-obj',f'SYMROOT={output}/{mode}-sym',f'DSTROOT={output}/{mode}-dst']
(output/f'{mode}-command.json').write_text(json.dumps(args,indent=2)+'\n')
with (output/f'{mode}-build.log').open('w') as log:
    result = subprocess.run(args,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
print('RELEASE reference exit',result.returncode,'log',output/f'{mode}-build.log',flush=True)
if result.returncode:
    raise SystemExit(result.returncode)
# Forced exports the built objects cannot provide: remove them from this private copy and link again
# (the symbols are absent from the comparison kernel either way; the second link stops the forced-export
# list from failing it).
objects = (output / f'{mode}-obj/RELEASE_ARM64_BCM2837/link.filelist').read_text().splitlines()
names = set()
for i in range(0, len(objects), 100):
    listed = subprocess.run(['xcrun', 'nm', '-gUj', *objects[i:i + 100]], capture_output=True, text=True, check=True)
    names.update(symbol for symbol in listed.stdout.splitlines() if symbol.startswith('_') and ' ' not in symbol)
removed = []
for filename in ('Private.exports', 'Private.arm64.exports'):
    path = output / 'source/config' / filename
    lines = path.read_text().splitlines(keepends=True)
    rejected = {line.strip() for line in lines
                if line.strip().startswith('_') and ':' not in line and not any(fnmatch.fnmatchcase(n, line.strip()) for n in names)}
    removed.extend(sorted(rejected))
    path.write_text(''.join(line for line in lines if line.strip() not in rejected))
import json as _json
record = output / 'omitted-unavailable-forced-exports.json'
previous = _json.loads(record.read_text()) if record.exists() else []
record.write_text(_json.dumps(sorted(set(previous + removed)), indent=2) + chr(10))
print('removed', len(removed), 'unavailable forced exports; linking again')
with (output / f'{mode}-build.log').open('a') as log:
    result = subprocess.run(args, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
print('RELEASE reference exit', result.returncode, 'log', output / f'{mode}-build.log', flush=True)
if result.returncode:
    raise SystemExit(result.returncode)
import shutil as _shutil
built = output / f'{mode}-sym/RELEASE_ARM64_BCM2837/mach.release.bcm2837.unstripped.noctf'
_shutil.copyfile(built, final)
print('reference', final)
