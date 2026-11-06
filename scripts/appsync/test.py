#!/usr/bin/env python3
"""Host regressions and optional build against the real, pinned OS inputs."""
import argparse
import hashlib
import json
import plistlib
import shutil
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from macho import add_dylib
import build
import signer

ROOT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fixture():
    name = b'/System/Library/Frameworks/Foundation.framework/Foundation\0'
    length = (24 + len(name) + 7) & ~7
    header = struct.pack('<8I', 0xfeedfacf, 0x100000c, 0x80000002, 2, 1, length, 0, 0)
    command = struct.pack('<6I', 0xc, length, 24, 0, 0, 0) + name
    return header + command.ljust(length, b'\0') + b'CODE AND CHAINED FIXUPS'


class MachOTests(unittest.TestCase):
    def test_dependency_preserves_header_ordinals_and_code(self):
        original = fixture()
        patched = add_dylib(original, build.DYLIB, digest(original))
        self.assertEqual(len(original), len(patched))
        self.assertEqual(original[:56], patched[:56])
        self.assertEqual(original[-22:], patched[-22:])
        self.assertEqual(patched.count(build.DYLIB.encode()), 1)

    def test_foreign_or_modified_os_rejected(self):
        with self.assertRaisesRegex(ValueError, 'source pin'):
            add_dylib(fixture() + b'changed', build.DYLIB, digest(fixture()))

    def test_bad_command_and_duplicate_dependency_rejected(self):
        data = bytearray(fixture())
        struct.pack_into('<I', data, 36, 0)
        with self.assertRaisesRegex(ValueError, 'size'):
            add_dylib(data, build.DYLIB, digest(data))
        data = add_dylib(fixture(), build.DYLIB, digest(fixture()))
        with self.assertRaisesRegex(ValueError, 'already present'):
            add_dylib(data, build.DYLIB, digest(data))

    def test_truncated_commands_and_long_name_rejected(self):
        for data in (fixture()[:20], fixture()[:40]):
            with self.assertRaises(ValueError):
                add_dylib(data, build.DYLIB, digest(data))
        with self.assertRaisesRegex(ValueError, 'does not fit'):
            add_dylib(fixture(), '/' + 'x' * 256, digest(fixture()))


def runtime_tests(work):
    dylib = work / 'AppSync.dylib'
    flags = ['-fobjc-arc', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-framework', 'Foundation',
             '-fsanitize=address,undefined']
    build.run('xcrun', 'clang', *flags, '-DAS_HOST_TEST=1', '-dynamiclib', ROOT / 'AppSync.m', '-Wl,-undefined,dynamic_lookup', '-o', dylib)
    # No applications, identifiers, hashes or policy section are passed to the builder.
    paths = [('/private/var/containers/Bundle/Application/NEW/Unseen.app', 'user'),
             ('/var/containers/Bundle/Application/NEW/Unseen.app/Frameworks/New.framework', 'user'),
             ('/private/var/installd/Library/Caches/staging/Another.app/PlugIns/Widget.appex', 'user'),
             ('/private/var/mobile/Media/PublicStaging/Third.app', 'user'),
             ('/System/Library/CoreServices/SpringBoard.app', 'system'),
             ('/private/var/ngpu/appsync/helper', 'system'),
             ('/private/var-other/Unseen.app', 'system'),
             ('/private/var/X.app/../../System/Invalid.app', 'system')]
    for process in ('installd', 'com.apple.MobileInstallationHelperService', 'SpringBoard'):
        binary = work / process
        build.run('xcrun', 'clang', *flags, ROOT / 'test-runtime.m', '-o', binary)
        for path, scope in paths:
            build.run(binary, dylib, path, scope)


def trust_tests(work, device):
    # Extract the complete new source file from the actual ordered kernel patch.
    patch = (device / 'patches/xnu-12377/sheng-appsync-user-trust.patch').read_text()
    section = patch.split('+++ b/bsd/kern/appsync_trust.inc\n', 1)[1].split('diff --git ', 1)[0]
    source = ''.join(line[1:] + '\n' for line in section.splitlines() if line.startswith('+'))
    assert 'appsync_trust_user_code' in source
    (work / 'appsync_trust.inc').write_text(source)
    binary = work / 'test-trust'
    build.run('xcrun', 'clang', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
              '-fsanitize=address,undefined', '-pthread', '-I', work, ROOT / 'test-trust.c', '-o', binary)
    build.run(binary)


def signing_tests(work):
    signing_tool = work / 'ldid'
    signer.build(signing_tool, host=True)
    harness = work / 'test-signing'
    build.run('xcrun', 'clang', '-fobjc-arc', '-fblocks', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
              '-fsanitize=address,undefined', '-framework', 'Foundation',
              '-DAS_SIGNER_PATH="' + str(signing_tool) + '"', ROOT / 'Signing.m', ROOT / 'test-signing.m', '-o', harness)
    base = work / 'Base.app'
    framework = base / 'Frameworks/Kit.framework'
    extension = base / 'PlugIns/Widget.appex'
    for bundle, name, identifier, kind in ((base, 'Main', 'org.unixnu.fixture', 'APPL'),
            (framework, 'Kit', 'org.unixnu.fixture.kit', 'FMWK'),
            (extension, 'Widget', 'org.unixnu.fixture.widget', 'XPC!')):
        bundle.mkdir(parents=True, exist_ok=True)
        (bundle / 'Info.plist').write_bytes(plistlib.dumps(dict(CFBundleIdentifier=identifier,
            CFBundleExecutable=name, CFBundleVersion='1', CFBundlePackageType=kind)))
        (bundle / 'resource.txt').write_text('original resource')
    source = work / 'main.c'
    source.write_text('int main(void) { return 0; }\n')
    sdk = build.run('xcrun', '--sdk', 'iphoneos', '--show-sdk-path', capture=True).stdout.strip()
    binaries = ['Main', 'Frameworks/Kit.framework/Kit', 'PlugIns/Widget.appex/Widget']
    entitlement_file = work / 'entitlements.plist'
    entitlements = {'application-identifier': 'EXAMPLE.org.unixnu.fixture', 'get-task-allow': True}
    entitlement_file.write_bytes(plistlib.dumps(entitlements))
    for name in reversed(binaries):
        binary = base / name
        build.run('xcrun', 'clang', '-target', 'arm64-apple-ios17.0', '-isysroot', sdk,
                  *(['-dynamiclib'] if binary.name == 'Kit' else []), source, '-o', binary)
        build.sign(binary, 'org.unixnu.fixture.' + binary.name, entitlement_file)
    build.run(signing_tool, '-Hsha256', '-M', '-S', base)
    original = build.sha(base / 'Main')
    build.run(harness, base, 'valid')
    assert original == build.sha(base / 'Main')

    unsigned = work / 'Unsigned.app'
    shutil.copytree(base, unsigned)
    for name in binaries:
        build.run('codesign', '--remove-signature', unsigned / name)
    for resource in unsigned.glob('**/_CodeSignature'):
        shutil.rmtree(resource)
    build.run(harness, unsigned, 'repair')
    for name in binaries:
        build.run('codesign', '--verify', '--strict', unsigned / name)

    modified = work / 'Modified.app'
    shutil.copytree(base, modified)
    (modified / 'Frameworks/Kit.framework/resource.txt').write_text('new resource')
    (modified / 'embedded.mobileprovision').write_bytes(b'expired profile fixture')
    (modified / 'PlugIns/Widget.appex/embedded.mobileprovision').write_bytes(b'expired nested profile')
    build.run(harness, modified, 'repair')
    assert not list(modified.glob('**/embedded.mobileprovision'))
    assert build.entitlements(modified / 'Main') == entitlements
    assert build.entitlements(modified / 'PlugIns/Widget.appex/Widget') == entitlements

    universal = work / 'Universal.app'
    shutil.copytree(base, universal)
    arm64e = work / 'arm64e'
    build.run('xcrun', 'clang', '-target', 'arm64e-apple-ios17.0', '-isysroot', sdk, source, '-o', arm64e)
    build.run('codesign', '--remove-signature', universal / 'Main')
    build.run('codesign', '--remove-signature', arm64e)
    fat = work / 'fat'
    build.run('xcrun', 'lipo', '-create', universal / 'Main', arm64e, '-output', fat)
    shutil.copyfile(fat, universal / 'Main')
    build.run(harness, universal, 'repair')
    for arch in ('arm64', 'arm64e'):
        build.run('codesign', '--verify', '--strict', '-a', arch, universal / 'Main')

    openssl = '/opt/homebrew/opt/openssl@3/bin/openssl'
    for name, days in [('FakeIdentity', '365'), ('Expired', '-1')]:
        key, request, certificate, identity = (work / (name + suffix) for suffix in ('.key', '.csr', '.crt', '.p12'))
        build.run(openssl, 'req', '-new', '-newkey', 'rsa:2048', '-nodes', '-keyout', key, '-out', request,
                  '-subj', '/CN=UniXNU Test/OU=EXAMPLE', capture=True)
        build.run(openssl, 'x509', '-req', '-in', request, '-signkey', key, '-out', certificate, *(['-not_before', '20200101000000Z', '-not_after', '20210101000000Z'] if name == 'Expired' else ['-days', days]), capture=True)
        if name == 'Expired':
            assert subprocess.run([openssl, 'x509', '-in', str(certificate), '-checkend', '0'], capture_output=True).returncode != 0
        build.run(openssl, 'pkcs12', '-export', '-inkey', key, '-in', certificate, '-out', identity, '-passout', 'pass:fixture', capture=True)
        app = work / (name + '.app')
        shutil.copytree(base, app)
        build.run(signing_tool, '-K' + str(identity), '-Ufixture', '-M', '-S', app)
        build.run(harness, app, 'repair')
        display = build.run('codesign', '-d', '--verbose=4', app / 'Main', capture=True).stderr
        assert 'Signature=adhoc' in display
        assert build.entitlements(app / 'Main') == entitlements

    linked = work / 'Linked.app'
    shutil.copytree(base, linked)
    (linked / 'outside').symlink_to(work / 'main.c')
    before = build.sha(linked / 'Main')
    build.run(harness, linked, 'reject')
    assert build.sha(linked / 'Main') == before

    encrypted = work / 'Encrypted.app'
    shutil.copytree(base, encrypted)
    code = bytearray((encrypted / 'Main').read_bytes())
    count, size = struct.unpack_from('<II', code, 16)
    at = 32
    for _ in range(count):
        command, length = struct.unpack_from('<II', code, at)
        if command == 0x2c:
            struct.pack_into('<I', code, at + 16, 1)
            break
        at += length
    else:
        # The minimal linked fixture can lack an encryption command; append it
        # in zero header padding, leaving executable data at its original offset.
        at = 32 + size
        assert code[at:at+24] == bytes(24)
        code[at:at+24] = struct.pack('<6I', 0x2c, 24, 0, 0, 1, 0)
        struct.pack_into('<II', code, 16, count + 1, size + 24)
    (encrypted / 'Main').write_bytes(code)
    before = build.sha(encrypted / 'Main')
    build.run(harness, encrypted, 'reject')
    assert build.sha(encrypted / 'Main') == before
    print('PASS: unsigned/fat/nested code, fake/expired identities, resource/profile repair, entitlement preservation, encrypted and escaping-symlink rejection')


def target_tests(os_root, output, os_image=None):
    build.build(os_root, output)
    report = json.loads((output / 'report.json').read_text())
    assert report['scope'] == 'all-user-bundles' and report['dynamic_user_trust']
    assert 'enrolled_bundles' not in report and 'app_cdhashes' not in report
    if os_image:
        runtime_integration(os_image, output / 'runtime')


def modules(path):
    data = path.read_bytes()
    count = struct.unpack_from('<I', data)[0]
    starts = list(struct.unpack_from(f'<{count}I', data, 4)) + [len(data)]
    return [data[starts[i]:starts[i + 1]] for i in range(count)]


def runtime_integration(os_image, output):
    output.mkdir(parents=True, exist_ok=True)
    addon, trust, seed = (output / name for name in ('input-addon.bin', 'input-trust.bundle', 'data.fixture'))
    addon.write_bytes(b'NGPUADD2' + struct.pack('<IIQ', 0, 0, 24))
    original = struct.pack('<I16sI', 2, bytes(16), 1) + bytes.fromhex('12' * 20) + bytes([2, 0, 0, 0])
    trust.write_bytes(struct.pack('<II', 1, 8) + original)
    seed.write_bytes(b'preserved Data input fixture')
    request = dict(output=str(output), data_ramdisk=str(seed), gpu_addon=str(addon), trust_cache=str(trust),
                   appsync=True, target='ios27', build='24A446', os_image=str(os_image))
    source = ROOT.parent / 'build-boot-runtime.py'
    request_file = output / 'request.json'
    for iteration in range(2):
        request_file.write_text(json.dumps(request))
        build.run(sys.executable, source, '--request', request_file)
        generated = json.loads((output / 'generated.json').read_text())
        trust_modules = modules(Path(generated['trust_cache']))
        assert trust_modules[0] == original and len(trust_modules) == 2
        report = json.loads((output / 'appsync-service.json').read_text())
        hashes = {m[24 + i * 24:44 + i * 24].hex() for m in trust_modules
                  for i in range(struct.unpack_from('<I', m, 20)[0])}
        assert report['scope'] == 'all-user-bundles'
        assert 'enrolled_bundles' not in report
        assert {file['cdhash'] for file in report['files'].values()} <= hashes
        assert seed.read_bytes() == b'preserved Data input fixture'
        request.update(gpu_addon=generated['gpu_addon'], trust_cache=generated['trust_cache'])
    print('PASS: runtime addon/trust integration, original module and Data preservation, repeat-build idempotence')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', type=Path, default=ROOT.parents[2] / 'UniXNU-sheng')
    parser.add_argument('--signing', action='store_true', help='build the host signer and exercise automatic signature repair')
    parser.add_argument('--os-root', type=Path)
    parser.add_argument('--os-image', type=Path, help='also exercise the full runtime packer and trust merge')
    parser.add_argument('--output', type=Path, default=ROOT.parents[1] / 'build/appsync-check')
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MachOTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    with tempfile.TemporaryDirectory(prefix='appsync-runtime-') as td:
        runtime_tests(Path(td))
        trust_tests(Path(td), args.device.resolve())
        if args.signing:
            signing_tests(Path(td))
    if args.os_root:
        target_tests(args.os_root.resolve(), args.output.resolve(), args.os_image.resolve() if args.os_image else None)
    print('PASS: Mach-O guards and production hooks under ASan/UBSan' +
          ('; signed arm64e adapter, native executable copies and global user-app scope' if args.os_root else ''))
