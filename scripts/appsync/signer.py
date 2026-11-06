#!/usr/bin/env python3
"""Build the pinned on-device ldid signer and its static dependencies."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parent
SOURCES = json.loads((ROOT / 'signer-sources.json').read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def build(output, host=False):
    # Resolve through scripts/appsync to share the cache with the assembled tree.
    cache = ROOT.parents[1] / '.cache/appsync-signer'
    cache.mkdir(parents=True, exist_ok=True)
    sdk_name = 'macosx' if host else 'iphoneos'
    sdk = subprocess.check_output(['xcrun', '--sdk', sdk_name, '--show-sdk-path'], text=True).strip()
    target = 'arm64-apple-macos12.0' if host else 'arm64-apple-ios27.0'
    identity = dict(sources=SOURCES, builder=sha(__file__), sdk=sdk, target=target,
                    ldid_patch=sha(ROOT / 'ldid-adhoc.patch'), compiler=subprocess.check_output(['xcrun', 'clang', '--version'], text=True))
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:16]
    destination = cache / key
    binary, report = destination / 'unixnu-ldid', destination / 'build.json'
    if report.is_file() and binary.is_file() and json.loads(report.read_text())['sha256'] == sha(binary):
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(binary, output)
        output.chmod(0o755)
        return json.loads(report.read_text())
    archives = cache / 'sources'
    archives.mkdir(exist_ok=True)

    def fetch(item):
        name, record = item
        archive = archives / (record['directory'] + '.tar.gz')
        if not archive.is_file():
            with urllib.request.urlopen(record['url'], timeout=120) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != record['sha256']:
                raise ValueError('source archive digest mismatch: ' + name)
            archive.write_bytes(data)
        if sha(archive) != record['sha256']:
            raise ValueError('source archive digest mismatch: ' + name)
        return name, archive

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        fetched = dict(pool.map(fetch, SOURCES.items()))
    destination.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='build-', dir=destination) as tmp:
        work = Path(tmp)
        sources = {}
        for name, archive in fetched.items():
            with tarfile.open(archive) as source:
                source.extractall(work, filter='data')
            sources[name] = work / SOURCES[name]['directory']
        flags = ['-target', target, '-isysroot', sdk, '-O2']
        crypto_key = hashlib.sha256(json.dumps([SOURCES['openssl'], sdk, target, identity['compiler']]).encode()).hexdigest()[:16]
        crypto = cache / ('crypto-' + crypto_key)
        crypto_record = crypto / 'sha256'
        if not (crypto_record.is_file() and (crypto / 'libcrypto.a').is_file() and
                crypto_record.read_text() == sha(crypto / 'libcrypto.a')):
            build_dir = work / 'crypto'
            build_dir.mkdir()
            env = dict(os.environ, CC='xcrun clang', CFLAGS=' '.join(flags),
                       AR='xcrun ar', RANLIB='xcrun ranlib')
            run('perl', sources['openssl'] / 'Configure', 'darwin64-arm64-cc',
                'no-shared', 'no-tests', 'no-apps', 'no-asm', 'no-module', 'no-engine',
                '--prefix=' + str(build_dir / 'install'), cwd=build_dir, env=env)
            run('make', '-j' + str(min(os.cpu_count() or 4, 8)), 'build_libs', cwd=build_dir, env=env)
            crypto.mkdir(exist_ok=True)
            shutil.copytree(sources['openssl'] / 'include', crypto / 'include', dirs_exist_ok=True)
            shutil.copytree(build_dir / 'include', crypto / 'include', dirs_exist_ok=True)
            shutil.copyfile(build_dir / 'libcrypto.a', crypto / 'libcrypto.a')
            crypto_record.write_text(sha(crypto / 'libcrypto.a'))
        plist = sources['libplist']
        config = work / 'config.h'
        config.write_text('\n'.join('#define ' + name + ' 1' for name in (
            'HAVE_STRDUP', 'HAVE_STRNDUP', 'HAVE_STRERROR', 'HAVE_GMTIME_R', 'HAVE_LOCALTIME_R',
            'HAVE_TIMEGM', 'HAVE_STRPTIME', 'HAVE_MEMMEM', 'HAVE_TM_TM_GMTOFF', 'HAVE_TM_TM_ZONE',
            '__LITTLE_ENDIAN__')) + '\n#define PACKAGE_VERSION "2.7.0"\n')
        objects = []
        for source in sorted((plist / 'src').glob('*.c')) + sorted((plist / 'libcnary').glob('*.c')):
            obj = work / (source.stem + '.o')
            run('xcrun', 'clang', *flags, '-DHAVE_CONFIG_H', '-DLIBPLIST_STATIC', '-I', work,
                '-I', plist / 'include', '-I', plist / 'src', '-I', plist / 'libcnary/include', '-c', source, '-o', obj)
            objects.append(obj)
        run('xcrun', 'ar', 'rcs', work / 'libplist.a', *objects)
        ldid = sources['ldid']
        run('patch', '-p1', '-i', ROOT / 'ldid-adhoc.patch', cwd=ldid)
        run('xcrun', 'clang++', *flags, '-std=c++11', '-DLDID_VERSION="UniXNU-af86971"',
            '-I', ldid, '-I', crypto / 'include', '-I', plist / 'include',
            '-c', ldid / 'ldid.cpp', '-o', work / 'ldid.o')
        run('xcrun', 'clang++', *flags, work / 'ldid.o', crypto / 'libcrypto.a',
            work / 'libplist.a', '-o', work / 'unixnu-ldid')
        shutil.copyfile(work / 'unixnu-ldid', binary)
        binary.chmod(0o755)
        # Keep relinkable objects for the statically linked LGPL dependency.
        shutil.copyfile(work / 'libplist.a', destination / 'libplist.a')
        shutil.copyfile(work / 'ldid.o', destination / 'ldid.o')
        shutil.copyfile(crypto / 'libcrypto.a', destination / 'libcrypto.a')
        licenses = destination / 'licenses'
        licenses.mkdir(exist_ok=True)
        for name, candidates in {'ldid': ['COPYING', 'LICENSE'], 'openssl': ['LICENSE.txt'],
                                 'libplist': ['COPYING.LESSER', 'COPYING']}.items():
            for filename in candidates:
                source = sources[name] / filename
                if source.is_file():
                    shutil.copyfile(source, licenses / (name + '-' + filename))
        record = dict(identity, sha256=sha(binary), cache=str(destination))
        report.write_text(json.dumps(record, indent=2) + '\n')
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(binary, output)
    output.chmod(0o755)
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output.resolve(), args.host), indent=2))
