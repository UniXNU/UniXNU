#!/usr/bin/env python3
"""Compile the generic platform expert against the actual source-kernel ABI."""
import argparse
import json
import tomllib
from pathlib import Path
import subprocess
import sys

from kernel_target import ARCH, TRIPLE, check_object

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
catalog = {entry['id']: entry for entry in tomllib.loads((ROOT / 'components.toml').read_text())['component']
           if entry['kind'] == 'driver' and any(name.endswith('.cpp') for name in entry.get('source_files', []))}
aliases = {entry.get('legacy_name', identifier): identifier for identifier, entry in catalog.items()}
auxiliary = ['NativeLegacyDisplay', 'NativeGOPPresenter', 'NativeOfflineGPU', 'NativeOfflineAccelerator', 'NativeIOGPUProviderProbe']
parser.add_argument('component', choices=sorted(set(catalog) | set(aliases) | set(auxiliary)))
parser.add_argument('--negative-aes-kat', action='store_true', help='Isolated own-source wrong-answer refusal control; never changes original inputs')
parser.add_argument('--verified-root', action='store_true', help='Authenticate all actual disk reads against an independently signed immutable policy')
parser.add_argument('--verified-root-bundle', action='store_true', help='Select exactly one capacity-matching policy per device, then independently authenticate it')
parser.add_argument('--negative-verified-block', action='store_true', help='Negative own-buffer control: corrupt only the completed DMA snapshot')
args = parser.parse_args()
identifier = aliases.get(args.component, args.component)
if identifier == 'ShengUfs' and ARCH == 'arm64e':
    if any((args.negative_aes_kat, args.verified_root, args.verified_root_bundle, args.negative_verified_block)):
        parser.error('The source UFS runtime always uses the authenticated policy bundle of the OS profile')
    raise SystemExit(subprocess.call([sys.executable, ROOT / 'scripts/build-sheng-source-storage.py', '--tree', ROOT]))
metadata = catalog.get(identifier, {})
runtime = metadata.get('legacy_name', identifier)
args.component = runtime
if args.verified_root_bundle and not args.verified_root:
    parser.error('A policy bundle requires verified block mode')
if args.verified_root_bundle and args.negative_verified_block:
    parser.error('Select either bundle policy qualification or the isolated DMA snapshot fault')
if (args.verified_root or args.negative_verified_block) and args.component != 'NativeVirtioBlock':
    parser.error('Verified block mode requires the concrete read-only block transport')
if args.negative_verified_block and not args.verified_root:
    parser.error('The isolated input fault requires verified block mode')
component = args.component
recipe = ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json'
record = json.loads(recipe.read_text().strip().rstrip(','))
directory = 'GopFramebuffer' if runtime in ('NativeLegacyDisplay', 'NativeGOPPresenter') else 'AdrenoMetal' if runtime in ('NativeOfflineGPU', 'NativeOfflineAccelerator', 'NativeIOGPUProviderProbe') else identifier
filename = next((name for name in metadata.get('source_files', []) if name.endswith('.cpp')), runtime + '.cpp')
source = ROOT / 'drivers' / directory / filename
outputs = metadata.get('outputs', [])
archive_output = next((path for path in outputs if path.endswith('.a')), None)
aux_dirs = {'NativeLegacyDisplay':'native-legacy-display', 'NativeGOPPresenter':'native-gop-presenter',
            'NativeOfflineGPU':'native-offline-gpu', 'NativeOfflineAccelerator':'native-offline-accelerator',
            'NativeIOGPUProviderProbe':'native-original-provider'}
out = ROOT / Path(archive_output or outputs[0]).parent if outputs else ROOT / 'build' / aux_dirs[runtime]
if args.verified_root:
    out = ROOT / ('build/virtio-mmio-block-verified-fault' if args.negative_verified_block else 'build/virtio-mmio-block-verified')
    if args.verified_root_bundle:
        out = ROOT / 'build/virtio-mmio-block-verified-bundle'
out.mkdir(parents=True, exist_ok=True)
if args.negative_aes_kat:
    if component != 'NativeAES':
        parser.error('The own-source KAT control requires NativeAES')
    out = ROOT / 'build/software-aes-kat-negative'
    out.mkdir(parents=True, exist_ok=True)
    text = source.read_text()
    marker = '0x76,0x49,0xab,0xac'
    if text.count(marker) != 1:
        raise SystemExit('The exact own-source NIST answer was not uniquely identified')
    (out / 'OriginalAESABI.h').write_bytes(source.with_name('OriginalAESABI.h').read_bytes())
    source = out / 'NativeAES.cpp'
    source.write_text(text.replace(marker, '0x77,0x49,0xab,0xac'))
destination = out / (component + '.o')
arguments = record['arguments']
command = []
index = 0
while index < len(arguments):
    value = arguments[index]
    if value == record['file']:
        command.append(str(source))
    elif value == '-o':
        command.extend(['-o', str(destination)])
        index += 1
    elif value == '-Xclang' and arguments[index + 1].startswith('-W'):
        index += 1
    elif not value.startswith('-W'):
        command.append(value)
    index += 1
command.extend(['-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
                '-Wno-c99-designator', '-Wno-reorder-init-list', '-Wno-deprecated-enum-enum-conversion',
                '-Wno-unnecessary-virtual-specifier', '-I', str(ROOT / '.cache/xnu-work/osfmk')])
if component in ('NativeVirtioBlock', 'NativeRamBlock', 'NativeUfs'):
    command += ['-I', str(ROOT / 'build/storage-abi/include')]
    if args.verified_root:
        command += ['-I', str(ROOT / 'kits/VerifiedRoot/include'), '-DNATIVE_VERIFIED_BLOCK=1']
    if args.negative_verified_block:
        command += ['-DNATIVE_VERIFIED_BLOCK_INJECT_FAULT=1']
    if args.verified_root_bundle:
        command += ['-DNATIVE_VERIFIED_BLOCK_MULTI_POLICY=1']
if component == 'NativeUfs':
    command += ['-I', str(ROOT / 'kits/VerifiedRoot/include'), '-I', str(ROOT / 'drivers/VirtioMmioBlock'),
                '-DNATIVE_VERIFIED_BLOCK=1', '-DNATIVE_VERIFIED_BLOCK_MULTI_POLICY=1', '-mgeneral-regs-only']
if component=='NativeOfflineGPU':
    command += ['-I',str(ROOT/'drivers/VirtioMmioConsole')]
if component in ('NativeLegacyDisplay','NativeHidInput'):
    command += ['-I', str(out)]
if component == 'NativeAdreno':
    command += ['-I', str(ROOT / 'kits/ArmSmmu4K'), '-I', str(ROOT / 'kits/AdrenoPM4'),
                '-I', str(ROOT / 'kits/sheng'), '-I', str(ROOT / 'kits/Sm8550Platform'), '-I', str(ROOT / 'kits/AdrenoFirmware'),
                '-I', str(ROOT / 'build/sheng-gmu'), '-I', str(ROOT / 'build/adreno740/include')]
(out / 'compile-command.json').write_text(json.dumps(command, indent=2) + '\n')
result = subprocess.run(command, cwd=record['directory'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
(out / 'compile.log').write_text(result.stdout)
if result.returncode:
    # The errors first (each with the four lines after it), then the tail: a build with many warnings pushed the errors out of
    # the last 3500 characters, the only part CI logs kept.
    lines = result.stdout.splitlines()
    errors = [n for n, line in enumerate(lines) if ' error: ' in line or line.startswith('error:')]
    excerpt = '\n'.join('\n'.join(lines[n:n + 5]) for n in errors[:10])
    raise SystemExit((excerpt + '\n...\n' if excerpt else '') + result.stdout[-3500:])
check_object(destination.read_bytes(), component)
archive = out / ('lib' + identifier + '.a')
archive.unlink(missing_ok=True)
subprocess.run(['xcrun', 'ar', 'rcs', archive, destination], check=True)
print(f'{identifier}: -Werror build and {TRIPLE} object audit passed')
