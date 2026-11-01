#!/usr/bin/env python3
"""Build payload runtime inputs from a pinned IPSW and the selected sources.

Invoked by unixnu.runtime with a JSON request; no device ID or private binary is
stored in source control. Existing Data seeds are copied into no writable mount.
"""
import argparse
import contextlib
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
    hashes = []
    for executable in executables:
        run('codesign', '--verify', '--strict', executable)
        detail = subprocess.run(['codesign', '--display', '--verbose=4', str(executable)],
                                check=True, capture_output=True, text=True).stderr
        match = re.search(r'^CDHash=([0-9a-f]{40})$', detail, re.M)
        if not match:
            raise SystemExit('no CDHash for ' + str(executable))
        hashes.append(match[1])
    return sorted(set(hashes))


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
