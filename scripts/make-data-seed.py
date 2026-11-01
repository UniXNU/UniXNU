#!/usr/bin/env python3
"""Create a first-install APFS Data seed from a read-only IPSW OS mount.

The resulting seed is installation state. Keep it for subsequent builds: APFS
UUIDs and transaction metadata make a new invocation a different installation.
"""
import argparse
import json
import os
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'drivers/DarwinBoot/Test'))
import packed_ramdisk


def merge(mount, home, name, values):
    path = mount / home / 'Library/Preferences' / (name + '.plist')
    path.parent.mkdir(parents=True, exist_ok=True)
    content = plistlib.loads(path.read_bytes()) if path.is_file() else {}
    content.update(values)
    path.write_bytes(plistlib.dumps(content, fmt=plistlib.FMT_BINARY))
    path.chmod(0o644)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('os_mount', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--gib', type=int, required=True)
    parser.add_argument('--build', required=True)
    parser.add_argument('--skip-setup', action='store_true')
    args = parser.parse_args()
    source = args.os_mount / 'private/var'
    if not (args.os_mount / 'sbin/launchd').is_file() or not source.is_dir():
        parser.error('not an IPSW OS volume')
    if args.output.exists():
        parser.error('refuse to overwrite an existing installation seed')
    if not 3 <= args.gib <= 1024:
        parser.error('--gib must be in 3..1024')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='new-data-', dir=args.output.parent) as td:
        work = Path(td)
        raw = work / 'seed.cdr'
        subprocess.run(['hdiutil', 'create', '-size', '32m', '-layout', 'NONE', '-fs', 'APFS',
                        '-volname', 'Data', '-type', 'UDTO', raw], check=True)
        mount = work / 'mount'
        mount.mkdir()
        attached = plistlib.loads(subprocess.check_output(['hdiutil', 'attach', '-nobrowse', '-owners', 'off',
                                                           '-mountpoint', mount, '-plist', raw]))
        device = attached['system-entities'][0]['dev-entry']
        try:
            for current, dirs, files in os.walk(source, followlinks=False):
                dirs[:] = [name for name in dirs if name != 'staged_system_apps']
                dest = mount / Path(current).relative_to(source)
                dest.mkdir(exist_ok=True)
                dest.chmod(stat.S_IMODE(Path(current).stat().st_mode))
                for name in list(dirs) + files:
                    src, dst = Path(current) / name, dest / name
                    if src.is_symlink():
                        dst.symlink_to(os.readlink(src))
                        if name in dirs:
                            dirs.remove(name)
                    elif src.is_file():
                        shutil.copy2(src, dst)
            for name in ('keybags', 'mobile/tmp', 'tmp', 'run', 'containers/Bundle',
                         'containers/Data/System', 'containers/Shared/SystemGroup', 'containers/Temp'):
                (mount / name).mkdir(parents=True, exist_ok=True)
            (mount / 'tmp').chmod(0o1777)
            if args.skip_setup:
                merge(mount, 'mobile', 'com.apple.purplebuddy', dict(SetupDone=True,
                      SetupFinishedAllSteps=True, SetupVersion=11, daemonizeNeedsToRun=False))
                merge(mount, 'mobile', 'com.apple.purplebuddy.notbackedup', {name: False for name in (
                    'ShouldRunDiagnosticsMiniBuddy', 'ShouldRunHSA2MiniBuddy', 'ShouldRunKeychainSyncMiniBuddy',
                    'ShouldRunMesaMiniBuddy', 'ShouldRunPaymentMiniBuddy', 'ShouldRunStandardMiniBuddy', 'SilentICDPUpgrade')})
                merge(mount, 'mobile', 'com.apple.managedconfiguration.notbackedup',
                      dict(LockdownActivationIndicatesCloudConfigurationAvailable=False))
                merge(mount, 'mobile', 'com.apple.springboard', dict(BKNoWatchdogs=True,
                      FBLaunchWatchdogExceptions={'com.apple.purplebuddy': 100.0}, MCForceShowCloudConfigurationUI=False))
                merge(mount, 'mobile', 'com.apple.migration', dict(LastSystemVersion=args.build,
                      DMUserDataDisposition=dict(SyntheticDidUpgrade=False, buildVersion=args.build)))
            for home in ('root', 'mobile'):
                for name in ('backboardd', '.GlobalPreferences'):
                    merge(mount, home, name, dict(CAEnableDeepFramebuffer=False,
                          CAEnableFramebufferCompression=False, CAEnableIOSurfaceCompression=False))
        finally:
            subprocess.run(['hdiutil', 'detach', device], check=True)
        base = work / 'base.dbr'
        packed_ramdisk.pack(raw, base)
        candidate = work / 'data.dbr'
        subprocess.run([sys.executable, ROOT / 'scripts/seed-data-grow.py', '--gib', str(args.gib), base, candidate], check=True)
        candidate.replace(args.output)
    print(json.dumps(dict(output=str(args.output), first_install=True, preserve_for_future_builds=True)))


if __name__ == '__main__':
    main()
