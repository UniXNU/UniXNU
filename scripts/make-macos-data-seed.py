#!/usr/bin/env python3
"""Create a first-install macOS APFS Data seed from a read-only IPSW system volume mount.

OS is the mounted system volume or its disk image (attached read-only here). A new macOS Data volume holds the system volume's /System/Library/Templates/Data. The kernel mounts it
at /System/Volumes/Data and sets the firmlinks of /usr/share/firmlinks into it
(macos-owner-data-firmlinks.patch). The template's owners matter on macOS (root, and service accounts
such as _windowserver), so the copy keeps them: run this as root, for example with sudo. The seed is
installation state; keep it for later builds as make-data-seed.py describes.

The seed travels in every payload beside the kernel, and the packed format holds at most 256 MiB, so the
template (about 0.8 GiB) is not copied whole. Files below KEEP stay real files, as the system writes them;
every other file becomes a symbolic link to the same file in the system volume's template, as macOS does
for the paths of Data.symlink-patterns. The copy is made in a scratch volume first and copied again into
the seed's image, so the seed holds no blocks of the replaced files.

    sudo python3 scripts/make-macos-data-seed.py OS OUTPUT --gib N [--skip-setup]
"""
import argparse
import contextlib
import json
import os
from pathlib import Path
import plistlib
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'drivers/DarwinBoot/Test'))
import packed_ramdisk  # noqa: E402

TEMPLATE = 'System/Library/Templates/Data'
KEEP = ('private/', 'Users/', 'Library/Preferences/', 'Library/Keychains/')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('os', type=Path, help='system volume mount or its disk image')
    parser.add_argument('output', type=Path)
    parser.add_argument('--gib', type=int, required=True)
    parser.add_argument('--skip-setup', action='store_true',
                        help='mark Setup Assistant done (/private/var/db/.AppleSetupDone)')
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error('run as root: the Data template keeps its owners')
    if args.os.is_file():
        with os_mount(args.os) as point:
            build(parser, args, point)
    else:
        build(parser, args, args.os)


@contextlib.contextmanager
def os_mount(image):
    # As build-boot-runtime.py: reuse an existing read-only attachment of this image and leave it attached.
    info = plistlib.loads(subprocess.check_output(['hdiutil', 'info', '-plist']))
    for entry in info.get('images', []):
        if Path(entry.get('image-path', '')).resolve() != image.resolve():
            continue
        if entry.get('writeable', True):
            raise SystemExit('The IPSW OS image is already attached writable; require an unchanged read-only input')
        mounts = [Path(item['mount-point']) for item in entry.get('system-entities', [])
                  if item.get('mount-point') and (Path(item['mount-point']) / 'sbin/launchd').is_file()]
        if len(mounts) == 1:
            yield mounts[0]
            return
    with tempfile.TemporaryDirectory(prefix='macos-os-') as td:
        point = Path(td) / 'os'
        point.mkdir()
        attached = plistlib.loads(subprocess.check_output(['hdiutil', 'attach', '-readonly', '-nobrowse', '-noverify',
                                                           '-mountpoint', point, '-plist', image]))
        try:
            yield point
        finally:
            subprocess.run(['hdiutil', 'detach', attached['system-entities'][0]['dev-entry']], check=True)


SF_RESTRICTED = 0x00080000


def copy_template(template, mount):
    """ditto keeps owners, modes, flags, ACLs and extended attributes. With System Integrity Protection
    enabled no process here may set the restricted flag (or com.apple.rootless), so those entries are
    copied without it; any other copy error fails."""
    result = subprocess.run(['ditto', template, mount], stderr=subprocess.PIPE, text=True)
    unprotected = []
    for line in result.stderr.splitlines():
        prefix, separator, reason = line.rpartition(': ')
        destination = Path(prefix.removeprefix('ditto: '))
        try:
            source = template / destination.relative_to(mount)
        except ValueError:
            source = None
        if (not separator or reason != 'Operation not permitted' or source is None or
                not os.lstat(source).st_flags & SF_RESTRICTED):
            raise SystemExit(f'ditto failed: {result.stderr.strip()}')
        unprotected.append(str(destination.relative_to(mount)))
    if result.returncode and not unprotected:
        raise SystemExit(f'ditto failed with status {result.returncode}')
    counts = [sum(1 + len(dirs) + len(files) for _, dirs, files in os.walk(root)) for root in (template, mount)]
    # The mounted volume adds its own .fseventsd (removed before packing).
    if counts[1] - (1 if (mount / '.fseventsd').exists() else 0) < counts[0]:
        raise SystemExit(f'incomplete Data copy: {counts[1]} entries for {counts[0]} in the template')
    if unprotected:
        print(f'{len(unprotected)} restricted template entries copied without the restricted flag: '
              + ', '.join(sorted(unprotected)), file=sys.stderr)


def link_template_files(mount):
    """Replace every regular file outside KEEP with a link to its template copy, keeping its owner."""
    kept = linked = 0
    for current, _, files in os.walk(mount):
        for name in files:
            path = Path(current) / name
            relative = path.relative_to(mount).as_posix()
            st = os.lstat(path)
            if not stat.S_ISREG(st.st_mode) or relative.startswith(KEEP):
                kept += stat.S_ISREG(st.st_mode)
                continue
            if st.st_flags & ~SF_RESTRICTED & 0xffff0000:
                os.chflags(path, 0)  # a system flag (such as schg) would refuse the unlink
            path.unlink()
            os.symlink('/' + TEMPLATE + '/' + relative, path)
            os.lchown(path, st.st_uid, st.st_gid)
            linked += 1
    return kept, linked


@contextlib.contextmanager
def new_volume(path, size):
    subprocess.run(['hdiutil', 'create', '-size', size, '-layout', 'NONE', '-fs', 'APFS',
                    '-volname', 'Data', '-type', 'UDTO', path], check=True)
    mount = path.with_suffix('.mount')
    mount.mkdir()
    attached = plistlib.loads(subprocess.check_output(['hdiutil', 'attach', '-nobrowse', '-owners', 'on',
                                                       '-mountpoint', mount, '-plist', path]))
    try:
        yield mount
    finally:
        subprocess.run(['hdiutil', 'detach', attached['system-entities'][0]['dev-entry']], check=True)


def build(parser, args, os_mount):
    template = os_mount / TEMPLATE
    if not (os_mount / 'sbin/launchd').is_file() or not (os_mount / 'usr/share/firmlinks').is_file():
        parser.error('not a macOS IPSW system volume')
    if not template.is_dir():
        parser.error(f'no {TEMPLATE} in the system volume')
    if args.output.exists():
        parser.error('refuse to overwrite an existing installation seed')
    if not 3 <= args.gib <= 1024:
        parser.error('--gib must be in 3..1024')
    owner = os.environ.get('SUDO_UID'), os.environ.get('SUDO_GID')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='new-macos-data-', dir=args.output.parent) as td:
        work = Path(td)
        raw = work / 'seed.cdr'
        # The scratch volume takes the whole template (about 0.8 GiB); the seed's own image only the result.
        with new_volume(work / 'scratch.cdr', '2g') as scratch:
            copy_template(template, scratch)
            if args.skip_setup:
                done = scratch / 'private/var/db/.AppleSetupDone'
                done.touch()
                os.chown(done, 0, 0)
                done.chmod(0o644)
            kept, linked = link_template_files(scratch)
            for path in (scratch / '.fseventsd', scratch / '.Spotlight-V100'):
                subprocess.run(['rm', '-rf', path], check=True)
            with new_volume(raw, '512m') as mount:
                subprocess.run(['ditto', scratch, mount], check=True)
                for path in (mount / '.fseventsd', mount / '.Spotlight-V100'):
                    subprocess.run(['rm', '-rf', path], check=True)
        (work / 'scratch.cdr').unlink()
        print(f'{kept} template files copied, {linked} linked to /{TEMPLATE}', file=sys.stderr)
        base = work / 'base.dbr'
        packed_ramdisk.pack(raw, base)
        candidate = work / 'data.dbr'
        subprocess.run([sys.executable, ROOT / 'scripts/seed-data-grow.py', '--gib', str(args.gib), base, candidate],
                       check=True)
        if owner[0] and owner[1]:
            os.chown(candidate, int(owner[0]), int(owner[1]))
        candidate.replace(args.output)
    print(json.dumps(dict(output=str(args.output), first_install=True, preserve_for_future_builds=True)))


if __name__ == '__main__':
    main()
