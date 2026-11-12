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
import shutil
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
    return ROOT / 'build' / {'ios27': 'adreno-metal-plugin27', 'macos27': 'adreno-metal-plugin-macos27'}.get(target, 'adreno-metal-plugin')


def build_boot_shims(work, base=None):
    """macOS on a read-only root container: the owner apfs_boot_util (scripts/macos-boot-shims) below bootshim/ of the addon
    (BASE, or one of its own), which the kernel shows over apfs.fs/Contents/Resources with apfs-boot-shim=1."""
    tree = work / 'boot-shims'
    (tree / 'bootshim').mkdir(parents=True)
    exe = tree / 'bootshim/apfs_boot_util'
    sdk = subprocess.check_output(['xcrun', '--sdk', 'macosx', '--show-sdk-path'], text=True).strip()
    run('xcrun', '--sdk', 'macosx', 'clang', '-target', 'arm64e-apple-macos27.0', '-isysroot', sdk, '-O2', '-Wall', '-Werror',
        ROOT / 'scripts/macos-boot-shims/apfs_boot_util.c', '-o', exe)
    run('codesign', '--force', '--sign', '-', '--pagesize', '4096', '--identifier', 'org.unixnu.apfs_boot_util', exe)
    if base is None:
        base = work / 'boot-shims-empty.bin'
        base.write_bytes(b'NGPUADD2' + struct.pack('<IIQ', 0, 0, 24))
    addon = work / 'boot-shims.bin'
    script('addon-add-dir.py', base, addon, 'bootshim', tree / 'bootshim')
    return addon


def bundle_cdhash(path, options=()):
    detail = subprocess.run(['codesign', '--display', '--verbose=4', *options, str(path)],
                            check=True, capture_output=True, text=True).stderr
    match = re.search(r'^CDHash=([0-9a-f]{40})$', detail, re.M)
    if not match:
        raise SystemExit('no CDHash for ' + str(path))
    return match[1]


def verified_cdhash(path, detached=None):
    options = ['--detached', str(detached)] if detached else []
    run('codesign', '--verify', '--strict', *options, path)
    return bundle_cdhash(path, options)


def addon_hashes(path, work, system_bundles=(), system_executables=None):
    data = path.read_bytes()
    if data[:8] != b'NGPUADD2' or len(data) < 24 or struct.unpack_from('<Q', data, 16)[0] != len(data):
        raise SystemExit('invalid GPU addon')
    at, executables, system = 24, [], []
    # Unchanged OS bundles keep Apple's signature, which the host's strict check calls obsolete.
    system_prefixes = tuple(f'audio/{name}/' for name in system_bundles)
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
            unchanged = (system_executables or {}).get(name)
            if unchanged and hashlib.sha256(body).hexdigest() != unchanged:
                raise ValueError('original system executable changed in addon: ' + name)
            (system if unchanged or name.startswith(system_prefixes) else executables).append(output)
    if at != len(data) or not executables:
        raise SystemExit('invalid addon length or no executables')
    hashes = [verified_cdhash(executable) for executable in executables]
    hashes += [bundle_cdhash(executable) for executable in system]
    cache = work / 'xpc/launchd.plist'
    if cache.is_file():
        signature = cache.with_suffix('.plist.sig')
        if not signature.is_file():
            raise SystemExit('owner launchd cache requires its detached signature')
        hashes.append(verified_cdhash(cache, signature))
    return sorted(set(hashes))


def merge_launchd_cache(source, daemons, destination, job_environment=None, job_overrides=None):
    """Add owner jobs and board-selected environment values to the OS launchd cache."""
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
    if not added and not job_environment and not job_overrides:
        raise ValueError('no owner launchd jobs or selected OS job changes')
    assert all(merged[key] == value for key, value in original.items() if key != 'LaunchDaemons')
    assert all(jobs[key] == value for key, value in original['LaunchDaemons'].items())
    for label, environment in (job_environment or {}).items():
        matches = [jobs[key] for key, job in original['LaunchDaemons'].items() if job.get('Label') == label]
        if len(matches) != 1:
            raise ValueError(f'expected one OS launchd job for {label}, found {len(matches)}')
        if not isinstance(environment, dict) or not all(isinstance(value, str) for value in environment.values()):
            raise ValueError(f'launchd environment values for {label} must be strings')
        matches[0].setdefault('EnvironmentVariables', {}).update(environment)
    fields = {'UserName': str, 'EnableTransactions': bool, 'EnablePressuredExit': bool,
              'ThrottleInterval': int}
    for label, changes in (job_overrides or {}).items():
        matches = [jobs[key] for key, job in original['LaunchDaemons'].items() if job.get('Label') == label]
        if len(matches) != 1:
            raise ValueError(f'expected one OS launchd job for {label}, found {len(matches)}')
        if not changes or not isinstance(changes, dict) or not set(changes) <= fields.keys():
            raise ValueError('unsupported OS launchd job override: ' + label)
        for key, value in changes.items():
            if type(value) is not fields[key] or (key == 'ThrottleInterval' and value < 0):
                raise ValueError(f'invalid {key} for OS launchd job {label}')
            if key == 'UserName' and not re.fullmatch('[a-z_][a-z0-9_-]*', value):
                raise ValueError('invalid launchd user for ' + label)
        matches[0].update(changes)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # This dictionary is consumed by launchd's private cached-plist parser.
    # Use the platform serializer for its binary representation.
    destination.write_bytes(plistlib.dumps(merged, fmt=plistlib.FMT_XML, sort_keys=False))
    run('plutil', '-convert', 'binary1', destination)
    assert plistlib.loads(destination.read_bytes()) == merged
    return dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                output_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                original_jobs=len(original['LaunchDaemons']), added_jobs=added,
                original_entries_preserved=not job_environment and not job_overrides,
                job_environment=job_environment or {}, job_overrides=job_overrides or {}, serializer='Apple plutil binary1')


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
    want_addon = request.get('gpu_addon_enabled', True)
    with tempfile.TemporaryDirectory(prefix='prepare-', dir=out) as td:
        work = Path(td)
        if not seed.is_file() or (addon is None and want_addon):
            with os_mount(request['os_image'], work) as mount:
                if not seed.is_file():
                    if not request['init_data']:
                        raise SystemExit('refuse to generate Data without --init-data')
                    script('make-data-seed.py', mount, seed, '--gib', str(request['data_gib']),
                           '--build', request['build'], *(['--skip-setup'] if request.get('skip_setup') else []))
                if addon is None and want_addon:
                    plugin = build_plugin(request['target'])
                    extra = []
                    for profile in request.get('wallpapers', []):
                        destination = work / profile
                        script('make-wallpaper-overlay.py', mount, destination, profile)
                        extra += ['--wallpaper-floating' if profile.endswith('-floating') else '--wallpaper', destination]
                    candidate = work / 'gpuaddon.bin'
                    # macOS: the plugin goes to /Library/GPUBundles (GPUBundles/ files; the kernel writes and protects them).
                    if request['target'] == 'macos27':
                        extra += ['--prefix', 'GPUBundles']
                    script('make-gpu-addon.py', '--publish', '--no-daemon', *extra, candidate,
                           env=dict(os.environ, ADRENO_PLUGIN_DIR=str(plugin)))
                    if request.get('boot_shims'):
                        candidate = build_boot_shims(work, candidate)
                    if request.get('audio_tool'):
                        audio = work / 'audio'
                        run(sys.executable, Path(request['device']) / request['audio_tool'], audio, request['audio_target'])
                        combined = work / 'combined.bin'
                        # macOS: the audio server's own driver directory on Data (Library/ files of the addon).
                        prefix = ('Library/Audio/Plug-Ins/HAL' if request['target'] == 'macos27' else 'audio')
                        bundles = [f'{prefix}/ShengAudio.driver', audio / 'ShengAudio.driver']
                        # The overlay hides the system's plug-in directory from the audio server's listing,
                        # so a system plug-in the board needs is listed by carrying its unchanged bundle.
                        for name in request.get('audio_system_plugins', []):
                            bundles += [f'audio/{name}', Path(mount) / 'System/Library/Audio/Plug-Ins/HAL' / name]
                        script('addon-add-dir.py', candidate, combined, *bundles)
                        candidate = combined
                    addon = out / 'gpuaddon.bin'
                    candidate.replace(addon)
        if addon is None and not want_addon and request.get('boot_shims'):
            addon = out / 'boot-shims.bin'
            build_boot_shims(work).replace(addon)
        bluetooth_report = None
        if request.get('bluetooth_tool'):
            bluetooth = work / 'bluetooth'
            mount_work = work / 'bluetooth-os'
            mount_work.mkdir()
            with os_mount(request['os_image'], mount_work) as mount:
                component = request.get('bluetooth_component')
                run(sys.executable, Path(request['device']) / request['bluetooth_tool'],
                    bluetooth, request['bluetooth_target'], '--os-root', mount,
                    *(['--component', component] if component else []))
            bluetooth_report = json.loads((bluetooth / 'report.json').read_text())
            directories = []
            for prefix, relative in bluetooth_report['directories'].items():
                if (not prefix or Path(prefix).is_absolute() or '..' in Path(prefix).parts or
                    Path(relative).is_absolute() or '..' in Path(relative).parts):
                    raise ValueError('invalid Bluetooth runtime directory')
                directories += [prefix, bluetooth / relative]
            candidate = work / 'bluetooth-addon.bin'
            script('addon-add-dir.py', addon, candidate, *directories)
            addon = out / 'bluetooth-addon.bin'
            candidate.replace(addon)
            (out / 'bluetooth-service.json').write_bytes((bluetooth / 'report.json').read_bytes())
        if request.get('wifi_tool'):
            wifi = work / 'wifi'
            run(sys.executable, Path(request['device']) / request['wifi_tool'], wifi, request['wifi_target'])
            extra = []
            wifi_report = json.loads((wifi / 'report.json').read_text())
            if wifi_report.get('firmware_prefix'):
                extra += [wifi_report['firmware_prefix'], wifi / 'firmware']
            # A Bluetooth runtime without job overrides (macOS: the system's own jobs start it) needs no merged cache.
            if request.get('wifi_launchd_cache') or (bluetooth_report is not None and bluetooth_report.get('launchd_job_overrides')):
                cache_work = work / 'launchd-cache'
                cache_work.mkdir()
                with os_mount(request['os_image'], cache_work) as mount:
                    cache_report = merge_launchd_cache(mount / 'System/Library/xpc/launchd.plist',
                        wifi / 'daemons', wifi / 'xpc/launchd.plist', request.get('launchd_job_environment'),
                        bluetooth_report['launchd_job_overrides'] if bluetooth_report else None)
                cache_report.update(sign_launchd_cache(wifi / 'xpc/launchd.plist'))
                extra += ['xpc', wifi / 'xpc']
                (out / 'wifi-launchd-cache.json').write_text(json.dumps(cache_report, indent=2) + '\n')
            candidate = work / 'wifi-addon.bin'
            script('addon-add-dir.py', addon, candidate, request.get('wifi_bin_prefix', 'bin'), wifi / 'bin',
                   'etc/wifi', wifi / 'etc/wifi', wifi_report.get('daemons_prefix', 'daemons'), wifi / 'daemons', *extra)
            addon = out / 'wifi-addon.bin'
            candidate.replace(addon)
            (out / 'wifi-service.json').write_bytes((wifi / 'report.json').read_bytes())
        elif bluetooth_report is not None and bluetooth_report.get('launchd_job_overrides'):
            daemons = work / 'empty-daemons'
            daemons.mkdir()
            cache_work = work / 'bluetooth-cache'
            cache_work.mkdir()
            cache = work / 'bluetooth-xpc/launchd.plist'
            with os_mount(request['os_image'], cache_work) as mount:
                cache_report = merge_launchd_cache(mount / 'System/Library/xpc/launchd.plist',
                    daemons, cache, request.get('launchd_job_environment'), bluetooth_report['launchd_job_overrides'])
            cache_report.update(sign_launchd_cache(cache))
            candidate = work / 'bluetooth-cache-addon.bin'
            script('addon-add-dir.py', addon, candidate, 'xpc', cache.parent)
            addon = out / 'bluetooth-addon.bin'
            candidate.replace(addon)
            (out / 'bluetooth-launchd-cache.json').write_text(json.dumps(cache_report, indent=2) + '\n')
        # Firmware tools stage device firmware the board extracted beforehand (data, not executables) under one firmware/ prefix
        # of the Data addon; they read local inputs only.
        for tool in request.get('firmware_tools', []):
            stem = Path(tool).stem
            stage = work / ('firmware-' + stem)
            run(sys.executable, Path(request['device']) / tool, stage)
            staged = json.loads((stage / 'report.json').read_text())
            prefix, directory = staged['firmware_prefix'], staged['directory']
            if (Path(prefix).parts[:1] != ('firmware',) or '..' in Path(prefix).parts or Path(directory).is_absolute() or
                    '..' in Path(directory).parts):
                raise ValueError(f'invalid firmware directory from {tool}')
            candidate = work / ('firmware-' + stem + '-addon.bin')
            script('addon-add-dir.py', addon, candidate, prefix, stage / directory)
            addon = out / ('firmware-' + stem + '-addon.bin')
            candidate.replace(addon)
            (out / ('firmware-' + stem + '.json')).write_bytes((stage / 'report.json').read_bytes())
        appsync_report = None
        if request.get('appsync'):
            if (request.get('target'), request.get('build')) != ('ios27', '24A446'):
                raise ValueError('AppSync requires iPadOS 27 build 24A446')
            appsync = work / 'appsync'
            mount_work = work / 'appsync-os'
            mount_work.mkdir()
            with os_mount(request['os_image'], mount_work) as mount:
                script('appsync/build.py', '--os-root', mount, '--output', appsync)
            appsync_report = json.loads((appsync / 'report.json').read_text())
            directories = [arg for prefix, directory in appsync_report['directories'].items()
                           for arg in (prefix, appsync / directory)]
            candidate = work / 'appsync-addon.bin'
            script('addon-add-dir.py', addon, candidate, *directories)
            addon = out / 'appsync-addon.bin'
            candidate.replace(addon)
            (out / 'appsync-service.json').write_bytes((appsync / 'report.json').read_bytes())
        absent_report = None
        if request.get('target') == 'macos27' and addon is not None:
            # macOS: the stand-in the kernel runs in place of a daemon on its deny-exec list (scripts/absent-service), at
            # /private/var/ngpu/bin/unixnu-absentd; its hash joins the owner trust with the addon's other executables.
            absent = work / 'absent'
            script('absent-service/build.py', absent, 'macos27')
            absent_report = json.loads((absent / 'report.json').read_text())
            candidate = work / 'absent-addon.bin'
            script('addon-add-dir.py', addon, candidate, 'bin', absent / 'bin')
            addon = out / 'absent-addon.bin'
            candidate.replace(addon)
            (out / 'absent-service.json').write_bytes((absent / 'report.json').read_bytes())
            # macOS: .skipbuddy in the Data volume's user template (/Library/User Template/Non_localized, which createhomedir copies
            # into every new home). A new account's first login otherwise runs Setup Assistant's MiniBuddy (MiniLauncherPlugin sets
            # MiniBuddyLaunch unless the home holds .skipbuddy), which keeps loginwindow from starting the Dock and Finder; this
            # board has no activation or Apple account setup to offer there (macOS run42/run44). macOS-DroidVM makes each home
            # with the marker from a boot job; a job in /Library/LaunchDaemons starts only when loginwindow has launched, too late
            # for an automatic login (run44: 1.5 s after loginwindow had made the home).
            template = work / 'user-template'
            template.mkdir()
            (template / '.skipbuddy').write_bytes(b'\n')
            candidate = work / 'template-addon.bin'
            script('addon-add-dir.py', addon, candidate, 'Library/User Template/Non_localized', template)
            addon = out / 'template-addon.bin'
            candidate.replace(addon)
        test_scripts = os.environ.get('UNIXNU_MACOS_TEST')
        if request.get('target') == 'macos27' and addon is not None and test_scripts:
            # Unattended testing only (never set for a release): UNIXNU_MACOS_TEST names a directory with daemon.sh (run as root at
            # boot) and/or agent.sh (run in the user's session after login). They go to /private/var/ngpu/test with a launchd job
            # each, and write to /Users/Shared/unixnu-test, which the log reader mirrors afterwards.
            source = Path(test_scripts)
            staged, jobs_d, jobs_a = work / 'test', work / 'test-daemons', work / 'test-agents'
            for directory in (staged, jobs_d, jobs_a):
                directory.mkdir()
            for name, jobs, extra in (('daemon', jobs_d, {}), ('agent', jobs_a, {'LimitLoadToSessionType': 'Aqua'})):
                script_file = source / (name + '.sh')
                if not script_file.is_file():
                    continue
                (staged / (name + '.sh')).write_bytes(script_file.read_bytes())
                command = (f'/bin/mkdir -p /Users/Shared/unixnu-test; exec /bin/sh /private/var/ngpu/test/{name}.sh '
                           f'>> /Users/Shared/unixnu-test/{name}.log 2>&1')
                (jobs / f'org.unixnu.test.{name}.plist').write_bytes(plistlib.dumps(dict(
                    Label=f'org.unixnu.test.{name}', RunAtLoad=True, ProgramArguments=['/bin/sh', '-c', command], **extra),
                    fmt=plistlib.FMT_XML))
            candidate = work / 'test-addon.bin'
            script('addon-add-dir.py', addon, candidate, 'test', staged, 'Library/LaunchDaemons', jobs_d,
                   'Library/LaunchAgents', jobs_a)
            addon = out / 'test-addon.bin'
            candidate.replace(addon)
        if trust is not None and (request.get('wifi_tool') or bluetooth_report is not None or appsync_report is not None
                                  or absent_report is not None):
            # Keep every original module intact. Append only absent hashes;
            # rebuilding from a previously integrated addon stays idempotent.
            hashes = addon_hashes(addon, work / 'signed-addon', request.get('audio_system_plugins', ()),
                                  appsync_report['system_executables'] if appsync_report else None)
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
                candidate = work / 'runtime-trust.bundle'
                script('trust-append-module.py', trust, candidate, *missing)
                trust = out / ('appsync-owner-trust.bundle' if appsync_report else
                               'bluetooth-owner-trust.bundle' if bluetooth_report else 'wifi-owner-trust.bundle')
                candidate.replace(trust)
        if trust is None:
            original = work / 'apple-trust.bundle'
            script('bundle-ipsw-trust.py', original, *request['trust_modules'])
            hashes = addon_hashes(addon, work / 'addon', request.get('audio_system_plugins', ()),
                                  appsync_report['system_executables'] if appsync_report else None) if addon else []
            candidate = work / 'owner-trust.bundle'
            if hashes:
                script('trust-append-module.py', original, candidate, *hashes)
            else:
                original.replace(candidate)
            trust = out / 'owner-trust.bundle'
            candidate.replace(trust)
        (out / 'generated.json').write_text(json.dumps(dict(data_ramdisk=str(seed), gpu_addon=str(addon) if addon else None,
                                                          trust_cache=str(trust)), indent=2) + '\n')


if __name__ == '__main__':
    main()
