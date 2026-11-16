#!/usr/bin/env python3
"""Record where a build came from, right after `./unixnu build ...`.

    record-build-provenance.py LABEL [--core CORE] [--device DEVICE] [--uefi UEFI] [--output DIR] [--artifact PATH ...]

The build outputs record only their own hashes and arguments. This records, as JSON:

- the core, device and firmware repositories: HEAD, branch, every uncommitted tracked file (status and content hash), the
  hash of the whole `git diff HEAD`, untracked entries, and every submodule's recorded and checked-out revision and state;
- the local settings of unixnu.local.toml, with the chip ID reduced to "present";
- the toolchain (macOS, Xcode, clang, LLVM, LLD, Rust, Python, the Bison the Mesa build uses);
- the hashes of the build outputs (kernel, payload, boot image, Data seed, patch list), of the locally generated root policy
  files and of the firmware volume, the payload's kernel arguments and the selected component revisions;
- the hashes of the boot images given with --artifact.

The record goes to <output>/provenance/LABEL.json and to out/provenance/LABEL.json in this repository (git-ignored). Nothing is
written if the record holds the chip ID.
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ('sheng', 'macos-27.3-26C5035r', 'sheng_macos')
OUTPUTS = ['kernel/kernel.macho', 'kernel/kernel.json', 'kernel/kernel.map.json', 'payload/payload.img', 'payload/payload.json',
           'boot/boot.img', 'boot/boot.json', 'runtime/data.dbr', 'xnu-patches.list', 'xnu-inputs.json']
FIRMWARE = 'Build/shengPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def file_entry(path):
    path = Path(path)
    if not path.is_file():
        return {'path': str(path), 'present': False}
    stat = path.stat()
    return {'path': str(path), 'sha256': sha256_file(path), 'bytes': stat.st_size,
            'modified': datetime.datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec='seconds')}


def git(repo, *args, binary=False):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, check=False)
    if result.returncode:
        return None
    return result.stdout if binary else result.stdout.decode('utf-8', 'replace').strip()


def repo_state(repo, submodules=True):
    repo = Path(repo)
    state = {'path': str(repo.resolve()), 'head': git(repo, 'rev-parse', 'HEAD'),
             'branch': git(repo, 'rev-parse', '--abbrev-ref', 'HEAD')}
    uncommitted = []
    status = git(repo, 'status', '--porcelain=v1', '-z', '--untracked-files=no', '--ignore-submodules=all', binary=True) or b''
    for record in [r for r in status.split(b'\0') if r]:
        code, name = record[:2].decode().strip(), record[3:].decode('utf-8', 'replace')
        target = repo / name
        entry = {'status': code, 'path': name}
        if target.is_file():
            entry['sha256'] = sha256_file(target)
        uncommitted.append(entry)
    state['uncommitted'] = uncommitted
    diff = git(repo, 'diff', 'HEAD', '--binary', '--ignore-submodules=all', binary=True) or b''
    state['diff_sha256'] = hashlib.sha256(diff).hexdigest() if diff else None
    untracked = git(repo, 'status', '--porcelain=v1', '--untracked-files=normal', '--ignore-submodules=all') or ''
    state['untracked'] = sorted(line[3:] for line in untracked.splitlines() if line.startswith('??'))
    if submodules and (repo / '.gitmodules').is_file():
        modules = []
        paths = git(repo, 'config', '-f', '.gitmodules', '--get-regexp', r'submodule\..*\.path') or ''
        for line in paths.splitlines():
            path = line.split(' ', 1)[1]
            recorded = (git(repo, 'ls-tree', 'HEAD', path) or '').split()
            entry = {'path': path, 'recorded': recorded[2] if len(recorded) > 2 else None}
            if (repo / path / '.git').exists():
                inner = repo_state(repo / path, submodules=False)
                entry.update(checked_out=inner['head'], branch=inner['branch'], uncommitted=inner['uncommitted'],
                             diff_sha256=inner['diff_sha256'])
            else:
                entry['checked_out'] = None
            modules.append(entry)
        state['submodules'] = modules
    return state


def _redact(value, secrets):
    """Replace every unique_chip_id, at any depth, with {"present": true} and collect the values."""
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if key == 'unique_chip_id':
                secrets.append(str(item))
                out[key] = {'present': True}
            else:
                out[key] = _redact(item, secrets)
        return out
    if isinstance(value, list):
        return [_redact(item, secrets) for item in value]
    return value


def local_settings(path):
    path = Path(path)
    if not path.is_file():
        return {'present': False}, []
    secrets = []
    settings = _redact(tomllib.loads(path.read_text()), secrets)
    return settings, secrets


def build_setting(settings, key, default=None):
    """A setting at the top level or in the [build] table (unixnu.local.toml keeps them there)."""
    if key in settings:
        return settings[key]
    return settings.get('build', {}).get(key, default)


def command(*args):
    try:
        result = subprocess.run(list(args), capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'error': str(error)}
    text = (result.stdout or result.stderr).strip()
    return text.splitlines()[0] if text else {'error': f'exit {result.returncode}'}


def toolchain(output):
    bison = output / 'tree/.cache/mesa-tools/bin/bison'
    return {
        'macos': command('sw_vers', '-productVersion'), 'macos_build': command('sw_vers', '-buildVersion'),
        'xcode': command('xcodebuild', '-version'), 'xcode_clang': command('xcrun', 'clang', '--version'),
        'llvm_clang': command('/opt/homebrew/opt/llvm/bin/clang', '--version'),
        'lld': command('/opt/homebrew/opt/lld/bin/ld.lld', '--version'),
        'rust': command('rustc', '+1.98.0', '--version'), 'python': sys.version.split()[0],
        'mesa_bison': {'path': str(bison.resolve()) if bison.exists() else None,
                       'version': command(str(bison), '--version') if bison.exists() else None},
    }


def components():
    path = ROOT / 'components.toml'
    if not path.is_file():
        return {}
    data = tomllib.loads(path.read_text())
    items = data.get('component') or data.get('components') or []
    if isinstance(items, dict):
        items = list(items.values())
    return {item.get('id', item.get('path')): item.get('revision') for item in items if item.get('revision')}


def write_record(record, targets, secrets):
    text = json.dumps(record, indent=2, sort_keys=True) + '\n'
    lowered = text.lower()
    for secret in secrets:
        if secret and secret.lower() in lowered:
            raise SystemExit('record holds the chip ID; nothing written')
    for target in targets:
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    return text


def main():
    global ROOT
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('label', help='record name, for example cd6')
    parser.add_argument('--core', type=Path, help='core checkout owning the build settings')
    parser.add_argument('--device', type=Path, help='selected device checkout')
    parser.add_argument('--uefi', type=Path, help='selected firmware checkout')
    parser.add_argument('--output', type=Path, help='the build output directory (default: from unixnu.local.toml)')
    parser.add_argument('--artifact', type=Path, action='append', default=[], help='an image built from these outputs')
    args = parser.parse_args()
    ROOT = (args.core or ROOT).resolve()
    settings, secrets = local_settings(ROOT / 'unixnu.local.toml')
    if not secrets:
        raise SystemExit('unixnu.local.toml names no unique_chip_id; the record could not be checked for it')
    output = args.output or Path(build_setting(settings, 'out', ROOT / 'out')).joinpath(*PROFILE)
    if not (output / 'kernel').is_dir():
        raise SystemExit(f'{output}: no build output there (pass --output)')
    device = (args.device or ROOT / build_setting(settings, 'device', '../UniXNU-sheng')).resolve()
    uefi = (args.uefi or ROOT / build_setting(settings, 'uefi', '../uefi-sheng')).resolve()
    payload_json = output / 'payload/payload.json'
    policies = sorted((device / 'scripts/policies').glob('*/*/*')) if (device / 'scripts/policies').is_dir() else []
    patches = output / 'xnu-patches.list'
    record = {
        'label': args.label,
        'recorded': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
        'repositories': {'core': repo_state(ROOT), 'device': repo_state(device), 'firmware': repo_state(uefi)},
        'local_settings': settings,
        'toolchain': toolchain(output),
        'outputs': {name: file_entry(output / name) for name in OUTPUTS},
        'payload_kernel_args': json.loads(payload_json.read_text()).get('kernel_args') if payload_json.is_file() else None,
        'kernel_patches': patches.read_text().split() if patches.is_file() else None,
        'root_policies': {str(path.relative_to(device)): file_entry(path) for path in policies if path.is_file()},
        'firmware_volume': file_entry(uefi / FIRMWARE),
        'components': components(),
        'artifacts': [file_entry(path) for path in args.artifact],
    }
    targets = [output / 'provenance' / f'{args.label}.json', ROOT / 'out/provenance' / f'{args.label}.json']
    write_record(record, targets, secrets)
    for target in targets:
        print(target)


if __name__ == '__main__':
    main()
