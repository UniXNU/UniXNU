#!/usr/bin/env python3
"""Build the 24A446 AppSync adapter for all user applications."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import tempfile

from macho import add_dylib
import signer

ROOT = Path(__file__).resolve().parent
DYLIB = '/usr/lib/UniXNUAppSync.dylib'
HELPER = ('System/Library/PrivateFrameworks/MobileInstallation.framework/XPCServices/'
          'com.apple.MobileInstallationHelperService.xpc')
SPRINGBOARD = 'System/Library/CoreServices/SpringBoard.app'
# The kernel union-mounts coreservices over /System/Library/CoreServices. SpringBoard.app must stay an ordinary
# directory there: LaunchServices refuses a mount root as a bundle (isVolume), and SpringBoard aborts without its record.
SPRINGBOARD_COPY = 'coreservices/SpringBoard.app'
PINS = {
    'usr/libexec/installd': ('libexec/installd', '5c80de3423681dec4c8c16dce4d8dd86d26039e8d29639b8b2cd1f53d187aac1'),
    'usr/libexec/backboardd': ('libexec/backboardd', 'fbba7fd2925990dd859b24629ecab5cdbf6f2fac8c1c357ec0f9e412ded75559'),
    HELPER + '/com.apple.MobileInstallationHelperService':
        ('helper/com.apple.MobileInstallationHelperService', '154bb529fd044777c0f823740955f65b0ba96a169d3953df5d117e9b8b5e1914'),
    SPRINGBOARD + '/SpringBoard': ('coreservices/SpringBoard.app/SpringBoard', '85dfb1b386ee009dfc0b7eb914c66aa7646d062254d18881a99647b55d7ffaee'),
}
MACHO = (b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe', b'\xca\xfe\xba\xbf')


def run(*args, capture=False):
    return subprocess.run([str(arg) for arg in args], check=True,
                          capture_output=capture, text=capture)


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def details(path):
    result = run('codesign', '-d', '--verbose=4', path, capture=True).stderr
    return {name: re.search(r'^' + key + r'=(.+)$', result, re.M)[1]
            for name, key in (('cdhash', 'CDHash'), ('identifier', 'Identifier'))}


def entitlements(path):
    value = run('codesign', '-d', '--entitlements', ':-', path, capture=True).stdout
    return plistlib.loads(value.encode()) if value.strip() else {}


def sign(path, identifier=None, entitlement_file=None):
    options = ['--identifier', identifier] if identifier else ['--preserve-metadata=identifier,entitlements,flags']
    if entitlement_file:
        options += ['--entitlements', str(entitlement_file)]
    run('codesign', '--force', '--sign', '-', '--pagesize', '4096', '--digest-algorithm', 'sha256', *options, path)
    run('codesign', '--verify', '--strict', path)


def build(os_root, output):
    output.mkdir(parents=True, exist_ok=True)
    (output / 'report.json').unlink(missing_ok=True)
    # Preflight every input before creating executable outputs.
    patched = {dest: add_dylib((os_root / source).read_bytes(), DYLIB, pin)
               for source, (dest, pin) in PINS.items()}
    with tempfile.TemporaryDirectory(prefix='build-', dir=output) as temporary:
        work = Path(temporary)
        for directory in ('lib', 'libexec', 'helper', SPRINGBOARD_COPY):
            (work / directory).mkdir(parents=True)
        sdk = run('xcrun', '--sdk', 'iphoneos', '--show-sdk-path', capture=True).stdout.strip()
        flags = ['-target', 'arm64e-apple-ios27.0', '-isysroot', sdk, '-fobjc-arc', '-O2',
                 '-Wall', '-Wextra', '-Werror', '-framework', 'Foundation']
        run('xcrun', 'clang', *flags, '-dynamiclib', ROOT / 'AppSync.m', ROOT / 'Signing.m', ROOT / 'BacklightMode.m', '-install_name', DYLIB,
            '-Wl,-reexport_framework,Foundation', '-Wl,-compatibility_version,3000',
            '-Wl,-current_version,5027.0.69',
            '-o', work / 'lib/UniXNUAppSync.dylib')
        sign(work / 'lib/UniXNUAppSync.dylib', 'org.unixnu.appsync')
        signing = signer.build(work / 'libexec/unixnu-ldid')
        sign(work / 'libexec/unixnu-ldid', 'org.unixnu.ldid')
        shutil.copytree(Path(signing['cache']) / 'licenses', work / 'libexec/appsync-licenses')
        run('xcrun', 'clang', *flags, ROOT / 'appinst.m', '-o', work / 'libexec/unixnu-appinst')
        entitlement_file = work / 'appinst-entitlements.plist'
        entitlement_file.write_bytes(plistlib.dumps({
            'application-identifier': 'org.unixnu.appinst', 'platform-application': True,
            'com.apple.private.mobileinstall.allowedSPI': ['Install', 'InstallForLaunchServices'],
            'com.apple.security.exception.mach-lookup.global-name': ['com.apple.mobile.installd']}))
        sign(work / 'libexec/unixnu-appinst', 'org.unixnu.appinst', entitlement_file)
        # Sign complete bundles so Info.plist and resource envelopes remain
        # consistent when the copies appear at their original system paths.
        for source, dest in ((HELPER, 'helper'), (SPRINGBOARD, SPRINGBOARD_COPY)):
            shutil.copytree(os_root / source, work / dest, dirs_exist_ok=True)
            (work / dest / 'UniXNUAppSync.runtime').write_text('24A446\n')
        originals = {}
        for source, (dest, pin) in PINS.items():
            original, target = os_root / source, work / dest
            before = entitlements(original)
            identity = details(original)['identifier']
            target.write_bytes(patched[dest])
            target.chmod(0o755)
            sign(target)
            if entitlements(target) != before or details(target)['identifier'] != identity:
                raise ValueError('OS entitlements or identifier changed: ' + source)
            originals[source] = dict(sha256=pin, entitlements_preserved=True)
        files = {}
        for relative in ['lib/UniXNUAppSync.dylib', 'libexec/unixnu-appinst', 'libexec/unixnu-ldid', *patched]:
            path = work / relative
            files[relative] = dict(details(path), sha256=sha(path))
        system_executables = {}
        for original_dir, directory in ((HELPER, 'helper'), (SPRINGBOARD, SPRINGBOARD_COPY)):
            for path in (work / directory).rglob('*'):
                if not path.is_file() or path.relative_to(work).as_posix() in files:
                    continue
                with path.open('rb') as stream:
                    magic = stream.read(4)
                if magic in MACHO:
                    original = os_root / original_dir / path.relative_to(work / directory)
                    if sha(path) != sha(original):
                        raise ValueError('nested system executable changed')
                    system_executables['appsync/' + path.relative_to(work).as_posix()] = sha(original)
        report = dict(target='ios27', build='24A446', hardware_verified=False, originals=originals,
                      files=files, scope="all-user-bundles", dynamic_user_trust=True, signature_repair=True, signer=signing,
                      system_executables=system_executables,
                      directories={f'appsync/{name}': name for name in ('lib', 'libexec', 'helper', 'coreservices')})
        for directory in ('lib', 'libexec', 'helper', 'coreservices'):
            previous = output / directory
            if previous.exists():
                shutil.rmtree(previous)
            shutil.move(work / directory, previous)
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Built AppSync 24A446 adapter: all user bundles; {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--os-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.os_root.resolve(), args.output.resolve())
