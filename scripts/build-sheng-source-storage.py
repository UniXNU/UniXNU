#!/usr/bin/env python3
"""Build the arm64e source UFS runtime and its authenticated policy handoff.

The original IOStorageFamily and APFS stay in the kernel collection. Only the
public IOBlockStorageDevice implementation is compiled here; its metaclass is
registered late below the original class so the original storage driver can
match the source-backed device. Binary interface qualification is separate.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def helper(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def weak_defaults(source):
    """Zero weak definitions for the weak imports of a diagnostic source.

    The kernel link cannot leave weak imports undefined, so components that are
    not built in get these defaults; a component's own definition wins. Data is
    zero, functions report absence: int returns -1, strings "", other scalars 0, pointers NULL.
    Hidden visibility keeps the static kernel link from binding them at run time.
    """
    import re
    lines = []
    for line in source.read_text().splitlines():
        line = line.strip()
        if not (line.startswith('extern ') and line.endswith('__attribute__((weak_import));')):
            continue
        decl = line[len('extern '):-len('__attribute__((weak_import));')].replace('__attribute__((weak_import))', '').strip()
        call = re.match(r'^(.*?[\s*])([A-Za-z_]\w*)\s*\((.*)\)$', decl)
        if call and '(*' not in decl.split(call.group(2))[0]:
            ret = call.group(1).strip()
            body = ('' if ret == 'void' else ' return -1;' if ret == 'int' else
                    ' return "";' if ret.replace(' ', '') in ('constchar*', 'char*') else ' return 0;')
            lines.append(f'__attribute__((weak, visibility("hidden"))) {decl} {{{body} }}')
        else:
            lines.append(f'__attribute__((weak, visibility("hidden"))) {decl};')
    # Quoted headers are resolved next to the source, which the generated file is not.
    includes = [l.replace('#include "', f'#include "{source.parent}/') for l in source.read_text().splitlines()
                if l.startswith('#include')]
    # Element types the declarations name are defined in the source itself.
    named = set(re.findall(r'struct (\w+)', '\n'.join(lines)))
    includes += [m.group(0) for m in re.finditer(r'^struct (\w+) \{[^;{}]*(?:;[^;{}]*)*\};', source.read_text(), re.M)
                 if m.group(1) in named]
    # The defaults keep the declarations' unnamed parameters.
    pragma = ['#pragma clang diagnostic ignored "-Wc23-extensions"']
    return '\n'.join(includes + pragma + lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, default=ROOT)
    parser.add_argument('--device', type=Path)
    parser.add_argument('--storage-source', type=Path)
    parser.add_argument('--policy-dir', type=Path,
                        help='Directory containing OS/ and SystemOS/ signed policies and verification.json')
    args = parser.parse_args()
    tree = args.tree.resolve()
    device = (args.device or tree).resolve()
    storage = (args.storage_source or tree / 'refer/IOStorageFamily').resolve()
    # The OS profile names the root images ([root]); kernel.py passes them in the environment.
    build_id = os.environ.get('UNIXNU_IPSW_BUILD')
    if not build_id:
        parser.error('UNIXNU_IPSW_BUILD is not set; run through unixnu build kernel')
    policies = (args.policy_dir or tree / f'build/verified-root-{build_id}').resolve()
    # The resolved build tree links the device package as kits/sheng, while an
    # explicit device repository keeps package/ and drivers/ side by side.
    package_dirs = [device / 'package']
    if device != tree:
        package_dirs += [device / 'kits/sheng', tree / 'kits/sheng']
    else:
        package_dirs += [tree / 'kits/sheng']

    def device_source(relative, *extra):
        for directory in list(extra) + package_dirs + [device, tree]:
            candidate = directory / relative
            if candidate.is_file():
                return candidate
        parser.error(f'{relative} not found under the device or build tree')
    if os.environ.get('UNIXNU_XNU_ARCH', 'arm64e') != 'arm64e':
        parser.error('This adapter requires an arm64e iPadOS profile')
    os.environ['UNIXNU_XNU_ARCH'] = 'arm64e'
    if int(os.environ.get('UNIXNU_IOS_VERSION', '0').split('.')[0]) < 26:
        parser.error('This adapter requires iPadOS 26 or later')
    build = helper('source_compile', ROOT / 'scripts/build-sheng-source-drivers.py')
    headers = helper('source_headers', ROOT / 'scripts/prepare-storage-headers.py')
    target = helper('source_target', ROOT / 'scripts/kernel_target.py')
    out = tree / 'build/sheng-source-storage'
    out.mkdir(parents=True, exist_ok=True)
    header_report = headers.prepare(storage, '7edb88fbae296fb7c8ce2f64e115e116e566d51c', out / 'headers')
    # A bring-up image can carry one policy: the boot image must stay under the
    # 192 MiB fastboot limit, and the second table does not fit yet.
    tables_in_userdata = os.environ.get('XNU_SOURCE_STORAGE_TABLES', '') == 'userdata'
    selected = [name.strip() for name in (os.environ.get('UNIXNU_SOURCE_STORAGE_POLICIES') or os.environ.get('XNU_SOURCE_STORAGE_POLICIES', 'OS,SystemOS')).split(',')
                if name.strip() in ('OS', 'SystemOS')]
    if not selected:
        parser.error('UNIXNU_SOURCE_STORAGE_POLICIES names no policy')
    manifest_paths = [policies / name / 'manifest.bin' for name in selected]
    key = (policies / f'{selected[0]}/trusted-key.bin').read_bytes()
    if len(key) != 395 or any(key != (policies / f'{name}/trusted-key.bin').read_bytes() for name in selected):
        parser.error('All selected policies must share the same complete explicit owner anchor')
    manifests = []
    expected = {}
    for name, prefix in (('OS', 'UNIXNU_ROOT_OS'), ('SystemOS', 'UNIXNU_ROOT_SYSTEMOS')):
        digest, identity = os.environ.get(prefix + '_SHA256'), os.environ.get(prefix + '_UUID')
        if name in selected and not (digest and identity):
            parser.error(f'the OS profile has no [root] {name.lower()}_image_sha256 and {name.lower()}_volume_uuid')
        expected[name] = (digest, identity and identity.upper())
    for path in manifest_paths:
        verification = json.loads(path.with_name('verification.json').read_text())
        digest, identity = expected[path.parent.name]
        if (not verification['real_c_signature_and_block_verification'] or
                verification['image_sha256'] != digest or verification['volume_uuid'] != identity or
                verification['trusted_key_sha256'] != hashlib.sha256(key).hexdigest()):
            parser.error(f'{path.parent.name}: require complete verification of the actual {build_id} image')
        # With the tables in userdata only the 544-byte signed header goes into the boot image;
        # NativeUfs reads "<window>.vroot" from the root image and vr_open checks it against the header.
        # A policy directory may ship manifest.header.bin, the header without the block tables: every
        # check below still runs on it, and the full tables stay a local input of the userdata image.
        header = path.with_name('manifest.header.bin')
        if tables_in_userdata and header.is_file():
            data = header.read_bytes()
            if len(data) != 544 or data[56:88].hex() != digest:
                parser.error(f'{header}: policy header does not describe the selected image')
            manifests.append(data)
        else:
            data = path.read_bytes()
            if len(data) < 544 or data[56:88].hex() != digest:
                parser.error(f'{path}: manifest does not describe the selected image')
            manifests.append(data[:544] if tables_in_userdata else data)
    cursor = 32 + 16 * len(manifests)
    table = bytearray()
    for data in manifests:
        table += struct.pack('<QQ', cursor, len(data))
        cursor += len(data)
    bundle = struct.pack('<8sQQQ', b'VROOTB01', 1, len(manifests), cursor) + table + b''.join(manifests)
    (out / 'root-policies.bin').write_bytes(bundle)
    # Only the independent trust anchor is linked into the kernel. The large
    # signed hash tables are a separate firmware handoff, authenticated in XNU.
    boot_log_defaults = out / 'BootLogDefaults.c'
    boot_log_defaults.write_text(weak_defaults(device_source('BootLog.c')))
    anchor = out / 'RootAnchor.c'
    anchor.write_text('#include <stdint.h>\nconst uint8_t verified_root_key[395] = {' +
                      ','.join(str(b) for b in key) + '};\n')
    base = out / 'IOBlockStorageDevice.cpp'
    original = (storage / 'IOBlockStorageDevice.cpp').read_text()
    macro = 'OSDefineMetaClassAndAbstractStructors(IOBlockStorageDevice,IOService)'
    if original.count(macro) != 1:
        parser.error('Pinned IOBlockStorageDevice registration macro changed')
    base.write_text(original.replace(macro, '''
extern "C" const OSMetaClass *native_source_storage_parent(void);
OSDefineMetaClassWithInit(IOBlockStorageDevice, IOService, )
IOBlockStorageDevice::MetaClass::MetaClass()
    : OSMetaClass("UniXNUBlockStorageDevice", native_source_storage_parent(), sizeof(IOBlockStorageDevice)) {}
OSDefineAbstractStructors(IOBlockStorageDevice, IOService)
OSDefineOperatorMethods(IOBlockStorageDevice)
'''))
    obj = tree / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837'
    cpp = json.loads((obj / 'iokit/DEVELOPMENT/IOPlatformExpert.cpo.json').read_text().strip().rstrip(','))
    c = json.loads((obj / 'osfmk/DEVELOPMENT/startup.o.json').read_text().strip().rstrip(','))
    # BSD sources (sys/proc.h, the system calls) take kern_exec's flags.
    bsd = json.loads((obj / 'bsd/DEVELOPMENT/kern_exec.o.json').read_text().strip().rstrip(','))
    bsd_sources = {'BootWatchdogPolicy.c', 'BootDiagExport.c'}
    includes = ['-I', str(out / 'headers/include'), '-I', str(ROOT / 'kits/VerifiedRoot/include'),
                '-I', str(ROOT / 'drivers/VirtioMmioBlock'), '-I', str(tree / '.cache/xnu-work/osfmk')]
    flags = ['-DNATIVE_UFS_SOURCE_API=1', '-DNATIVE_VERIFIED_BLOCK=1',
             '-DNATIVE_VERIFIED_BLOCK_MULTI_POLICY=1', '-DNATIVE_VERIFIED_POLICY_HANDOFF=1']
    # The RAM disk carries the Data seed; like NativeUfs its class registers with the source storage classes.
    sources = [base, device / 'drivers/ShengUfs/NativeUfs.cpp', ROOT / 'drivers/RamBlock/NativeRamBlock.cpp',
               device_source('SourceStorage.cpp'), device_source('SourceRootPolicies.cpp'),
               device_source('SourceRootBinding.cpp'), device_source('BootLog.c'), boot_log_defaults, device_source('BootReset.c'),
               ROOT / 'kits/VerifiedRoot/src/verified_root.c',
               ROOT / 'kits/VerifiedRoot/adapters/xnu_crypto.c', anchor]
    if int(os.environ['UNIXNU_IOS_VERSION'].split('.')[0]) >= 27:
        # The source path does not run BootProgress's process worker. Reuse its
        # native capture code in a separate worker owned by the UFS log.
        flags.append('-DNATIVE_BOOT_PROCESS_CAPTURE=1')
        sources += [device_source(name) for name in
                    ('BootProcessProbe.c', 'BootUiTraceProbe.c', 'BootProcessWorker.c')]
        # The launchd job policy (sheng-disable-watchdogd, sheng-lite, sheng-disable-jobs, sheng-setup) that BootProgress carries on
        # iPadOS 17; the kernel runs it after the Data mount.
        sources.append(device_source('BootWatchdogPolicy.c'))
        # The diagnostic file export (sheng-diag-export): the unified log, crash reports and a screenshot, read through the VFS.
        sources.append(device_source('BootDiagExport.c'))
    objects, inputs = [], {}
    objcopy = shutil.which('llvm-objcopy') or '/opt/homebrew/opt/llvm/bin/llvm-objcopy'
    for source in sources:
        record = (bsd if source.name in bsd_sources else c) if source.suffix == '.c' else cpp
        output = out / (source.stem + '.o')
        command = build.compile_command(record, source, output, includes, flags)
        if source == base:
            command.append('-Wno-error')
        result = subprocess.run(command, cwd=record['directory'], text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out / (source.stem + '.command.json')).write_text(json.dumps(command, indent=2) + '\n')
        (out / (source.stem + '.log')).write_text(result.stdout)
        if result.returncode:
            raise SystemExit(result.stdout[-6000:])
        target.check_object(output.read_bytes(), source.name)
        if source.name in ('IOBlockStorageDevice.cpp', 'NativeUfs.cpp', 'NativeRamBlock.cpp'):
            late = output.with_suffix('.late.o')
            subprocess.run([objcopy, '--remove-section=__DATA,__mod_init_func',
                            f'--globalize-symbol=__GLOBAL__sub_I_{source.name}', output, late], check=True)
            output = late
        objects.append(output)
        inputs[str(source)] = build.sha(source)
    archive = out / 'libShengSourceStorage.a'
    archive.unlink(missing_ok=True)
    subprocess.run(['xcrun', 'ar', 'rcs', archive, *objects], check=True)
    # Keep the catalog's archive output stable for the resolved-tree copier.
    catalog_output = tree / 'build/sheng-ufs/libShengUfs.a'
    catalog_output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(archive, catalog_output)
    report = dict(archive=str(archive), archive_sha256=build.sha(archive), sources=inputs,
                  headers=header_report, target=target.TRIPLE,
                  policy_bundle_sha256=build.sha(out / 'root-policies.bin'),
                  trusted_key_sha256=hashlib.sha256(key).hexdigest(), runtime_qualified=False)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(archive)


if __name__ == '__main__':
    main()
