#!/usr/bin/env python3
"""Compile sheng storage/input against pinned public source interfaces.

Produces relocatable objects and archives only. It does not bind an original
IOKit family, emit a boot image, or qualify the family's private binary ABI.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_helper(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compile_command(record, source, output, includes, extra):
    arguments = record['arguments']
    command = [arguments[0], *includes]
    index = 1
    replaced = False
    while index < len(arguments):
        value = arguments[index]
        if value == record['file']:
            command.append(str(source))
            replaced = True
        elif value == '-o':
            command.extend(['-o', str(output)])
            index += 1
        elif value in ('-MF', '-MT', '-MQ', '-MJ'):
            index += 1
        elif value in ('-MD', '-MMD', '-MP'):
            pass
        elif value == '-Xclang' and arguments[index + 1].startswith('-W'):
            index += 1
        elif not value.startswith('-W'):
            command.append(value)
        index += 1
    if not replaced:
        raise SystemExit('Kernel compilation record does not contain its source argument')
    command += ['-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter']
    if source.suffix != '.c':
        command += ['-Wno-c99-designator', '-Wno-reorder-init-list',
                    '-Wno-deprecated-enum-enum-conversion', '-Wno-unnecessary-virtual-specifier']
    command += ['-mgeneral-regs-only', '-MD', '-MF', str(output.with_suffix('.d')), *extra]
    return command


def nm(path, mode):
    return set(subprocess.check_output(['xcrun', 'nm', '-j', mode, str(path)], text=True).splitlines())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', required=True, type=Path, help='Prepared XNU build tree')
    parser.add_argument('--device', required=True, type=Path, help='UniXNU-sheng checkout')
    parser.add_argument('--profile', type=Path, help='OS profile.toml (default: the os_profile of the device board.toml)')
    parser.add_argument('--storage-source', type=Path)
    parser.add_argument('--hid-source', type=Path)
    parser.add_argument('--touch-firmware', type=Path, help='Extracted Novatek firmware; defaults to the device cache')
    parser.add_argument('--with-storage-family', action='store_true',
                        help='Also compile the public IOStorageFamily kernel sources and generated IIG implementation')
    args = parser.parse_args()
    tree, device = args.tree.resolve(), args.device.resolve()
    if args.profile is None:
        board = tomllib.loads((device / 'board.toml').read_text())
        args.profile = ROOT / 'profiles/os' / board['board']['os_profile'] / 'profile.toml'
    profile = tomllib.loads(args.profile.read_text())
    pins = {entry['name']: entry for entry in profile.get('source', [])}
    for family in ('IOStorageFamily', 'IOHIDFamily'):
        if not pins.get(family, {}).get('commit'):
            parser.error(f'{args.profile}: missing explicit {family} source pin')
    os_profile = profile['os']
    os.environ['UNIXNU_XNU_ARCH'] = os_profile['arch']
    os.environ['UNIXNU_IOS_VERSION'] = os_profile['ios_version']
    target = load_helper('source_driver_target', ROOT / 'scripts/kernel_target.py')
    storage_helper = load_helper('source_storage_headers', ROOT / 'scripts/prepare-storage-headers.py')
    storage = (args.storage_source or tree / 'refer/IOStorageFamily').resolve()
    hid = (args.hid_source or tree / 'refer/IOHIDFamily').resolve()
    storage_helper.pinned_source(hid, pins['IOHIDFamily']['commit'])
    storage_helper.pinned_source(storage, pins['IOStorageFamily']['commit'])
    recipe = tree / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json'
    record = json.loads(recipe.read_text().strip().rstrip(','))
    c_recipe = tree / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/osfmk/DEVELOPMENT/startup.o.json'
    c_record = json.loads(c_recipe.read_text().strip().rstrip(','))
    # Audit the existing object too, before compiling with a possibly stale recipe.
    kernel_object = Path(record['directory']) / 'IOPlatformExpert.cpo'
    target.check_object(kernel_object.read_bytes(), 'Kernel compilation recipe')
    target.check_object((Path(c_record['directory']) / 'startup.o').read_bytes(), 'Kernel C compilation recipe')
    kernel = tree / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped'
    out = tree / 'build/sheng-source-drivers'
    out.mkdir(parents=True, exist_ok=True)
    manifest = out / 'report.json'
    manifest.unlink(missing_ok=True)
    header_report = storage_helper.prepare(storage, pins['IOStorageFamily']['commit'], out / 'headers')
    include = out / 'headers/include'
    for source_dir, relative in ((hid / 'IOHIDFamily', 'IOKit/hid'),
                                 (hid / 'IOHIDSystem/IOKit/hidsystem', 'IOKit/hidsystem')):
        destination = include / relative
        destination.mkdir(parents=True, exist_ok=True)
        for path in sorted(source_dir.glob('*.h')):
            shutil.copyfile(path, destination / path.name)
    sdk = Path(header_report['sdk'])
    sdk_kernel = sdk / 'System/Library/Frameworks/Kernel.framework/Versions/A/Headers'
    # XNU's own headers retain precedence. The SDK supplies generated HIDDriverKit
    # declarations missing from the source checkout; used inputs are hashed below.
    includes = ['-I', str(include), '-idirafter', str(sdk_kernel)]
    extra = ['-I', str(tree / '.cache/xnu-work/osfmk')]
    firmware = (args.touch_firmware or device / '.cache/firmware/novatek/novatek_nt36532_n81a_fw_csot.bin').resolve()
    data = firmware.read_bytes()
    if not data:
        raise SystemExit(f'{firmware}: empty touch firmware')
    firmware_source = out / 'NvtFirmware.c'
    firmware_source.write_text('/* Generated vendor firmware; build output only. */\n#include <stdint.h>\n'
                               f'const uint32_t native_touch_firmware_size = {len(data)};\n'
                               f'const uint8_t native_touch_firmware[{len(data)}] = {{' +
                               ','.join(str(value) for value in data) + '};\n')
    components = {
        'ShengUfs': [(device / 'drivers/ShengUfs/NativeUfs.cpp', [
            '-DNATIVE_VERIFIED_BLOCK=1', '-DNATIVE_VERIFIED_BLOCK_MULTI_POLICY=1',
            '-I', str(ROOT / 'kits/VerifiedRoot/include'), '-I', str(ROOT / 'drivers/VirtioMmioBlock')])],
        'ShengHidInput': [(device / 'drivers/ShengHidInput/NativeHidInput.cpp', ['-DNATIVE_HID_SOURCE_API=1'])],
        'ShengInputTransport': [(device / 'package/TouchProbe.cpp', [
            '-I', str(ROOT / 'drivers/QcomGeniSpi'), '-I', str(device / 'drivers/ShengNovatekTouch')]),
            (device / 'package/ButtonProbe.cpp', []),
            (ROOT / 'drivers/QcomGeniSpi/GeniSpi.c', []),
            (device / 'drivers/ShengNovatekTouch/NvtProtocol.c', []),
            (device / 'drivers/ShengNovatekTouch/NvtTouchCore.c', []),
            (firmware_source, [])],
    }
    generation = None
    if args.with_storage_family:
        generated = out / 'storage-generated'
        generated.mkdir(exist_ok=True)
        driver_sdk = Path(subprocess.check_output(['xcrun', '--sdk', 'driverkit', '--show-sdk-path'], text=True).strip())
        definition = storage / 'BlockStorageDeviceDriverKit/IOUserBlockStorageDevice.iig'
        header, implementation = generated / 'IOUserBlockStorageDevice.h', generated / 'IOUserBlockStorageDevice.iig.cpp'
        generate = ['xcrun', 'iig', '--def', str(definition), '--header', str(header),
                    '--impl', str(implementation), '--', '-x', 'c++', '-std=gnu++17',
                    '-fno-exceptions', '-fno-rtti', '-D__IIG=1', '-DPLATFORM_DriverKit=1',
                    '-isysroot', str(driver_sdk), '-iframework',
                    str(driver_sdk / 'System/DriverKit/System/Library/Frameworks'),
                    '-idirafter', str(driver_sdk / 'System/DriverKit/usr/include')]
        (generated / 'command.json').write_text(json.dumps(generate, indent=2) + '\n')
        result = subprocess.run(generate, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (generated / 'generate.log').write_text(result.stdout)
        if result.returncode:
            raise SystemExit(f'IIG generation failed:\n{result.stdout}')
        generation = dict(definition_sha256=sha(definition), header_sha256=sha(header),
                          implementation_sha256=sha(implementation), sdk=str(driver_sdk),
                          sdk_iig_inputs={str(p): sha(p) for p in sorted(driver_sdk.rglob('*.iig'))})
        # PBXSourcesBuildPhase of Apple's IOStorageFamily kernel target, plus
        # the implementation generated from its IIG input. Keep Apple source
        # warnings visible without treating them as errors in owned code.
        names = ['IOAppleLabelScheme', 'IOApplePartitionScheme', 'IOBlockStorageDevice',
                 'IOBlockStorageDriver', 'IOFDiskPartitionScheme', 'IOFilterScheme',
                 'IOGUIDPartitionScheme', 'IOMedia', 'IOMediaBSDClient', 'IOPartitionScheme',
                 'IORequest', 'IORequestsPool', 'IOStorage', 'IOUserBlockStorageDevice_kext']
        family_flags = ['-I', str(storage), '-I', str(generated), '-Wno-error']
        components['IOStorageFamily'] = [(storage / (name + '.cpp'), family_flags) for name in names]
        components['IOStorageFamily'].append((implementation, family_flags))
    kernel_exports = nm(kernel, '-gU')
    entries = {}
    for component, sources in components.items():
        objects, details = [], []
        archive = out / ('lib' + component + '.a')
        archive.unlink(missing_ok=True)
        for source, flags in sources:
            output = out / (source.stem + '.o')
            output.unlink(missing_ok=True)
            source_record = c_record if source.suffix == '.c' else record
            command = compile_command(source_record, source, output, includes, extra + flags)
            (out / (source.stem + '.command.json')).write_text(json.dumps(command, indent=2) + '\n')
            result = subprocess.run(command, cwd=source_record['directory'], text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (out / (source.stem + '.log')).write_text(result.stdout)
            if result.returncode:
                raise SystemExit(f'{source.name}: compile failed\n{result.stdout[-5000:]}')
            target.check_object(output.read_bytes(), source.name)
            dependencies = {}
            deptext = output.with_suffix('.d').read_text().replace('\\\n', '')
            for name in shlex.split(deptext.split(':', 1)[1]):
                path = Path(name)
                if not path.is_absolute():
                    path = Path(source_record['directory']) / path
                dependencies[str(path.resolve())] = sha(path)
            (out / (source.stem + '.inputs.json')).write_text(json.dumps(dependencies, indent=2) + '\n')
            imports = nm(output, '-u')
            details.append(dict(source=str(source), source_sha256=sha(source), object=str(output),
                                object_sha256=sha(output), undefined_symbols=sorted(imports),
                                warnings=sum('warning:' in line for line in result.stdout.splitlines())))
            objects.append(output)
        subprocess.run(['xcrun', 'ar', 'rcs', str(archive), *map(str, objects)], check=True)
        entries[component] = dict(archive=str(archive), archive_sha256=sha(archive), objects=details)
        print(f'PASS: {component}: {target.TRIPLE} relocatable objects')
    partial = out / 'source-drivers.partial.o'
    partial.unlink(missing_ok=True)
    link = ['xcrun', 'ld', '-r', '-arch', target.ARCH, '-platform_version', 'ios',
            target.IOS_VERSION, target.IOS_VERSION, '-o', str(partial), '-all_load',
            *[entry['archive'] for entry in entries.values()]]
    (out / 'partial-link-command.json').write_text(json.dumps(link, indent=2) + '\n')
    result = subprocess.run(link, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / 'partial-link.log').write_text(result.stdout)
    if result.returncode:
        raise SystemExit(f'Relocatable link failed:\n{result.stdout}')
    target.check_object(partial.read_bytes(), 'Combined source drivers')
    report = dict(profile=str(args.profile.resolve()), profile_sha256=sha(args.profile),
                  build_scripts={str(path): sha(path) for path in (
                      Path(__file__), ROOT / 'scripts/prepare-storage-headers.py', ROOT / 'scripts/kernel_target.py')},
                  target=target.TRIPLE, recipe=str(recipe), recipe_sha256=sha(recipe),
                  c_recipe=str(c_recipe), c_recipe_sha256=sha(c_recipe),
                  kernel=str(kernel), kernel_sha256=sha(kernel),
                  source_pins={name: pins[name] for name in ('IOStorageFamily', 'IOHIDFamily')},
                  sdk=str(sdk), components=entries,
                  storage_family_iig=generation,
                  touch_firmware=dict(path=str(firmware), sha256=sha(firmware), size=len(data)),
                  partial_link=dict(object=str(partial), sha256=sha(partial), passed=True),
                  unresolved_after_native_kernel=sorted(nm(partial, '-u') - kernel_exports),
                  compile_pass=True, link_qualified=False, runtime_qualified=False,
                  edge_gestures_qualified=False,
                  limitations=['Family imports have no target binding in this build.',
                               'HID diagnostics/startup and verified-root policy/crypto objects are not bundled.',
                               'Source HID mode does not install the Darwin 23 edge-event vtable patch.',
                               'macOS public source headers and generated SDK headers do not prove the iPadOS binary ABI.'])
    manifest.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Compile audit: {manifest}; linking and runtime remain unqualified')


if __name__ == '__main__':
    main()
