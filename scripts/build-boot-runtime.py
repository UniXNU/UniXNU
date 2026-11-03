#!/usr/bin/env python3
"""Build payload runtime inputs from a pinned IPSW and the selected sources.

Invoked by unixnu.runtime with a JSON request; no device ID or private binary is
stored in source control. Existing Data seeds are copied into no writable mount.
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import struct
import subprocess
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from mesa_patch_identity import validate_recorded_patches


def run(*command, **kwargs):
    subprocess.run([str(part) for part in command], check=True, **kwargs)


def script(name, *args, **kwargs):
    run(sys.executable, ROOT / 'scripts' / name, *args, **kwargs)


@contextlib.contextmanager
def os_mount(image, work):
    # A developer may already have this exact OS mounted for inspection. Reuse
    # only a read-only attachment, and leave its lifetime with its owner.
    info = plistlib.loads(subprocess.check_output(['hdiutil', 'info', '-plist']))
    for entry in info.get('images', []):
        if Path(entry.get('image-path', '')).resolve() != Path(image).resolve():
            continue
        if entry.get('writeable', True):
            raise SystemExit('The IPSW OS image is already attached writable; require an unchanged read-only input')
        mounts = [Path(item['mount-point']) for item in entry.get('system-entities', [])
                  if item.get('mount-point') and (Path(item['mount-point']) / 'sbin/launchd').is_file()]
        if len(mounts) == 1:
            yield mounts[0]
            return
    mount = work / 'os-mount'
    mount.mkdir()
    attached = plistlib.loads(subprocess.check_output(['hdiutil', 'attach', '-readonly', '-nobrowse',
                                                       '-mountpoint', str(mount), '-plist', str(image)]))
    device = attached['system-entities'][0]['dev-entry']
    try:
        yield mount
    finally:
        run('hdiutil', 'detach', device)


def checkout(path, pin):
    if not path.exists():
        path.mkdir(parents=True)
        run('git', 'init', '-q', path)
        run('git', '-C', path, 'fetch', '--depth=1', pin.get('mirror', pin['repository']), pin['commit'])
        run('git', '-C', path, 'checkout', '--detach', 'FETCH_HEAD')
        return True
    revision = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != pin['commit']:
        raise SystemExit(f'{path}: source revision differs from its pin; preserve and inspect the checkout')
    return False


def build_plugin(target):
    pins = json.loads((ROOT / 'scripts/data/adreno-compiler-inputs.json').read_text())
    mesa = ROOT / '.cache/mesa-work'
    fresh = checkout(mesa, pins['mesa'])
    if fresh:
        for patch in pins['patches']:
            run('git', '-C', mesa, 'apply', ROOT / patch)
    validate_recorded_patches(ROOT, mesa, pins)
    translator = json.loads((ROOT / 'scripts/data/gpu-metal-vulkan-inputs.json').read_text())['translator']
    checkout(ROOT / '.cache/gpu-reference/metal2vulkan', translator)
    venv = ROOT / '.cache/mesa-venv'
    if not (venv / 'bin/python').is_file():
        run(sys.executable, '-m', 'venv', venv)
    run(venv / 'bin/python', '-m', 'pip', 'install', '-r', ROOT / 'scripts/requirements-adreno-compiler.txt')
    script('build-turnip-darwin.py', '--target', target)
    # Replay is a diagnostic capture from a host GPU simulation, not a runtime
    # dependency. Do not require unrelated test fixtures in a release build.
    script('build-adreno-metal-plugin.py', '--target', target, '--no-replay')
    return ROOT / 'build' / ('adreno-metal-plugin27' if target == 'ios27' else 'adreno-metal-plugin')


def verified_cdhash(path, detached=None):
    options = ['--detached', str(detached)] if detached else []
    run('codesign', '--verify', '--strict', *options, path)
    detail = subprocess.run(['codesign', '--display', '--verbose=4', *options, str(path)],
                            check=True, capture_output=True, text=True).stderr
    match = re.search(r'^CDHash=([0-9a-f]{40})$', detail, re.M)
    if not match:
        raise SystemExit('no CDHash for ' + str(path))
    return match[1]


def addon_hashes(path, work):
    data = path.read_bytes()
    if data[:8] != b'NGPUADD2' or len(data) < 24 or struct.unpack_from('<Q', data, 16)[0] != len(data):
        raise SystemExit('invalid GPU addon')
    at, executables = 24, []
    for _ in range(struct.unpack_from('<I', data, 8)[0]):
        length, mode, size, packed = struct.unpack_from('<IIQQ', data, at)
        at += 24
        name = data[at:at + length - 1].decode()
        if not 1 < length <= 160 or name.startswith('/') or '..' in Path(name).parts:
            raise SystemExit('invalid addon path')
        at += (length + 7) & ~7
        body = zlib.decompress(data[at:at + packed])
        at += (packed + 7) & ~7
        if len(body) != size:
            raise SystemExit('invalid addon entry size')
        output = work / name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(body)
        output.chmod(mode & 0o777)
        if body[:4] in (b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe'):
            executables.append(output)
    if at != len(data) or not executables:
        raise SystemExit('invalid addon length or no executables')
    hashes = [verified_cdhash(executable) for executable in executables]
    cache = work / 'xpc/launchd.plist'
    if cache.is_file():
        signature = cache.with_suffix('.plist.sig')
        if not signature.is_file():
            raise SystemExit('owner launchd cache requires its detached signature')
        hashes.append(verified_cdhash(cache, signature))
    return sorted(set(hashes))


def merge_launchd_cache(source, daemons, destination):
    """Add owner jobs to the OS's precompiled launchd service dictionary."""
    original = plistlib.loads(source.read_bytes())
    merged = plistlib.loads(source.read_bytes())
    jobs = merged['LaunchDaemons']
    added = []
    for path in sorted(daemons.glob('*.plist')):
        job = plistlib.loads(path.read_bytes())
        if not job['Label'].startswith('org.unixnu.'):
            raise ValueError('owner service label required: ' + str(path))
        key = '/System/Library/LaunchDaemons/' + path.name
        if key in jobs:
            raise ValueError('OS launchd cache already owns ' + key)
        jobs[key] = job
        added.append(key)
    if not added:
        raise ValueError('no owner launchd jobs')
    assert all(merged[key] == value for key, value in original.items() if key != 'LaunchDaemons')
    assert all(jobs[key] == value for key, value in original['LaunchDaemons'].items())
    destination.parent.mkdir(parents=True, exist_ok=True)
    # This dictionary is consumed by launchd's private cached-plist parser.
    # Use the platform serializer for its binary representation.
    destination.write_bytes(plistlib.dumps(merged, fmt=plistlib.FMT_XML, sort_keys=False))
    run('plutil', '-convert', 'binary1', destination)
    assert plistlib.loads(destination.read_bytes()) == merged
    return dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                output_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                original_jobs=len(original['LaunchDaemons']), added_jobs=added,
                original_entries_preserved=True, serializer='Apple plutil binary1')


def sign_launchd_cache(path):
    """The unchanged OS cache loader checks this signature and its trust hash."""
    signature = path.with_suffix('.plist.sig')
    run('codesign', '--force', '--sign', '-', '--pagesize', '4096',
        '--digest-algorithm', 'sha256', '--identifier', 'org.unixnu.wifi.launchd-cache',
        '--detached', signature, path)
    return dict(cdhash=verified_cdhash(path, signature),
                detached_signature_sha256=hashlib.sha256(signature.read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    request = json.loads(parser.parse_args().request.read_text())
    out = Path(request['output'])
    seed = Path(request['data_ramdisk'])
    addon = Path(request['gpu_addon']) if request.get('gpu_addon') else None
    trust = Path(request['trust_cache']) if request.get('trust_cache') else None
    with tempfile.TemporaryDirectory(prefix='prepare-', dir=out) as td:
        work = Path(td)
        if not seed.is_file() or addon is None:
            with os_mount(request['os_image'], work) as mount:
                if not seed.is_file():
                    if not request['init_data']:
                        raise SystemExit('refuse to generate Data without --init-data')
                    script('make-data-seed.py', mount, seed, '--gib', str(request['data_gib']),
                           '--build', request['build'], *(['--skip-setup'] if request.get('skip_setup') else []))
                if addon is None:
                    plugin = build_plugin(request['target'])
                    extra = []
                    for profile in request.get('wallpapers', []):
                        destination = work / profile
                        script('make-wallpaper-overlay.py', mount, destination, profile)
                        extra += ['--wallpaper-floating' if profile.endswith('-floating') else '--wallpaper', destination]
                    candidate = work / 'gpuaddon.bin'
                    script('make-gpu-addon.py', '--publish', '--no-daemon', *extra, candidate,
                           env=dict(os.environ, ADRENO_PLUGIN_DIR=str(plugin)))
                    if request.get('audio_tool'):
                        audio = work / 'audio'
                        run(sys.executable, Path(request['device']) / request['audio_tool'], audio, request['audio_target'])
                        combined = work / 'combined.bin'
                        script('addon-add-dir.py', candidate, combined, 'audio/ShengAudio.driver', audio / 'ShengAudio.driver')
                        candidate = combined
                    addon = out / 'gpuaddon.bin'
                    candidate.replace(addon)
        if request.get('wifi_tool'):
            wifi = work / 'wifi'
            run(sys.executable, Path(request['device']) / request['wifi_tool'], wifi, request['wifi_target'])
            extra = []
            wifi_report = json.loads((wifi / 'report.json').read_text())
            if wifi_report.get('firmware_prefix'):
                extra += [wifi_report['firmware_prefix'], wifi / 'firmware']
            if request.get('wifi_launchd_cache'):
                cache_work = work / 'launchd-cache'
                cache_work.mkdir()
                with os_mount(request['os_image'], cache_work) as mount:
                    cache_report = merge_launchd_cache(mount / 'System/Library/xpc/launchd.plist',
                        wifi / 'daemons', wifi / 'xpc/launchd.plist')
                cache_report.update(sign_launchd_cache(wifi / 'xpc/launchd.plist'))
                extra += ['xpc', wifi / 'xpc']
                (out / 'wifi-launchd-cache.json').write_text(json.dumps(cache_report, indent=2) + '\n')
            candidate = work / 'wifi-addon.bin'
            script('addon-add-dir.py', addon, candidate, request.get('wifi_bin_prefix', 'bin'), wifi / 'bin',
                   'etc/wifi', wifi / 'etc/wifi', 'daemons', wifi / 'daemons', *extra)
            addon = out / 'wifi-addon.bin'
            candidate.replace(addon)
            (out / 'wifi-service.json').write_bytes((wifi / 'report.json').read_bytes())
            if trust is not None:
                # Keep every original module intact. Append only absent hashes;
                # rebuilding from a previously integrated addon stays idempotent.
                hashes = addon_hashes(addon, work / 'signed-addon')
                data = trust.read_bytes()
                count = struct.unpack_from('<I', data)[0]
                offsets = list(struct.unpack_from(f'<{count}I', data, 4)) + [len(data)]
                known = set()
                for index in range(count):
                    module = data[offsets[index]:offsets[index + 1]]
                    version, _, entries = struct.unpack_from('<I16sI', module)
                    stride = {0: 20, 1: 22, 2: 24}.get(version)
                    if stride is None or len(module) != 24 + entries * stride:
                        raise SystemExit('invalid original trust module')
                    known.update(module[24 + i * stride:44 + i * stride].hex() for i in range(entries))
                missing = sorted(set(hashes) - known)
                if missing:
                    candidate = work / 'wifi-trust.bundle'
                    script('trust-append-module.py', trust, candidate, *missing)
                    trust = out / 'wifi-owner-trust.bundle'
                    candidate.replace(trust)
        if trust is None:
            original = work / 'apple-trust.bundle'
            script('bundle-ipsw-trust.py', original, *request['trust_modules'])
            hashes = addon_hashes(addon, work / 'addon')
            candidate = work / 'owner-trust.bundle'
            script('trust-append-module.py', original, candidate, *hashes)
            trust = out / 'owner-trust.bundle'
            candidate.replace(trust)
        (out / 'generated.json').write_text(json.dumps(dict(data_ramdisk=str(seed), gpu_addon=str(addon),
                                                          trust_cache=str(trust)), indent=2) + '\n')


if __name__ == '__main__':
    main()
