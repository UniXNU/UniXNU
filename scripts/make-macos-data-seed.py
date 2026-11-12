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
for the paths of Data.symlink-patterns. The directories of READONLY, signed bundles that only system updates
change, become one link each to their template directory instead: a link inside a bundle points outside it,
and code signature validation (kernelmanagerd's kext validation of /Library/Apple) refuses such bundles.
The copy is made in a scratch volume first and copied again into the seed's image, so the seed holds no
blocks of the replaced files. --volume-uuid gives the Data volume the UUID the kernel mounts
(CONFIG_XNU_OWNER_DATA_VOLUME_UUID), so a new seed can replace an older one without a kernel build.

    sudo python3 scripts/make-macos-data-seed.py OS OUTPUT --gib N [--skip-setup] [--user NAME:PASSWORD [--auto-login]]
        [--volume-uuid UUID]

--skip-setup marks Setup Assistant done (/private/var/db/.AppleSetupDone: loginwindow shows its login window instead of Language
Chooser and Setup Assistant, which would also ask to activate the Mac) and writes a managed SkipSetupItems, so a new user's first
login skips Setup Assistant's per-user panes. --user adds a local administrator (uid 501, staff and admin, SALTED-SHA512-PBKDF2
shadow hash) to the directory (/private/var/db/dslocal), as macOS-DroidVM's stage-gpu-plugin.py does; loginwindow creates its home
on the first login. With --user the seed also holds that user's home, made from the user template, with .skipbuddy in it: a home that
loginwindow makes on the first login gets Setup Assistant's MiniBuddy (MiniLauncherPlugin sets MiniBuddyLaunch), which with every
pane skipped never finishes, so loginwindow never starts the Dock and Finder (macOS-DroidVM makes the home with a boot job for the
same reason; macOS run42: black screen behind the first MiniBuddy pane). --keyboard-type PRODUCT-VENDOR-COUNTRY=TYPE (decimal, may
repeat) records a keyboard's layout type in /Library/Preferences/com.apple.keyboardtype.plist (40 = ANSI), so Keyboard Setup
Assistant does not ask to identify it. --auto-login (unattended test seeds only, never a default) logs that user in at boot as System Settings'
"Automatically log in as" does: autoLoginUser in /Library/Preferences/com.apple.loginwindow.plist and /private/etc/kcpassword.
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import plistlib
import stat
import struct
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'drivers/DarwinBoot/Test'))
import packed_ramdisk  # noqa: E402

TEMPLATE = 'System/Library/Templates/Data'
KEEP = ('private/', 'Users/', 'Library/Preferences/', 'Library/Keychains/')
DSLOCAL = 'private/var/db/dslocal/nodes/Default'
SETUP_SKIP = 'Library/Managed Preferences/com.apple.SetupAssistant.managed.plist'
LOGINWINDOW_PREFS = 'Library/Preferences/com.apple.loginwindow.plist'
KCPASSWORD = 'private/etc/kcpassword'
KEYBOARD_TYPE = 'Library/Preferences/com.apple.keyboardtype.plist'
USER_TEMPLATE = 'Library/User Template'
KCPASSWORD_KEY = bytes.fromhex('7d895223d2bcddeaa3b91f')
SETUP_SKIP_ITEMS = ['Accessibility', 'AdditionalPrivacySettings', 'Appearance', 'AppleID', 'AppStore', 'Biometric', 'Diagnostics',
                    'DisplayTone', 'EnableLockdownMode', 'FileVault', 'iCloudDiagnostics', 'iCloudStorage', 'Intelligence', 'Location',
                    'OSShowcase', 'Privacy', 'Restore', 'Safety', 'ScreenTime', 'Siri', 'SoftwareUpdate', 'TermsOfAddress', 'TextSize',
                    'TOS', 'TouchIDPrompt', 'UnlockWithWatch', 'Wallpaper', 'Welcome']
READONLY = ('Library/Apple', 'Library/Application Support/Apple', 'Library/Documentation', 'Library/WebServer')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('os', type=Path, help='system volume mount or its disk image')
    parser.add_argument('output', type=Path)
    parser.add_argument('--gib', type=int, required=True)
    parser.add_argument('--skip-setup', action='store_true',
                        help='mark Setup Assistant done (/private/var/db/.AppleSetupDone)')
    parser.add_argument('--user', help='NAME:PASSWORD of a local administrator to add')
    parser.add_argument('--keyboard-type', action='append', default=[], metavar='PRODUCT-VENDOR-COUNTRY=TYPE',
                        help='a keyboard whose layout type is known (40 = ANSI); may repeat')
    parser.add_argument('--auto-login', action='store_true',
                        help='log the --user in at boot (unattended test seeds only)')
    parser.add_argument('--volume-uuid', type=uuid.UUID, help='the Data volume UUID (default: a new one)')
    args = parser.parse_args()
    if args.auto_login and not args.user:
        parser.error('--auto-login needs --user')
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


def link_template_directories(mount):
    """Replace each READONLY directory with one link to its template directory, keeping its owner."""
    for relative in READONLY:
        path = mount / relative
        if not path.is_dir() or path.is_symlink():
            continue
        st = os.lstat(path)
        subprocess.run(['chflags', '-R', 'nouchg,noschg', path], check=True)
        subprocess.run(['rm', '-rf', path], check=True)
        os.symlink('/' + TEMPLATE + '/' + relative, path)
        os.lchown(path, st.st_uid, st.st_gid)


def remove_volume_logs(mount):
    """The host's fseventsd and Spotlight state of a scratch volume. fseventsd may still be writing its log as it is removed
    ("Directory not empty"), so it is told to stop first (no_log) and the removal is retried."""
    for name in ('.fseventsd', '.Spotlight-V100'):
        path = mount / name
        if name == '.fseventsd' and path.is_dir():
            (path / 'no_log').touch()
        for attempt in range(10):
            if subprocess.run(['rm', '-rf', path]).returncode == 0 and not path.exists():
                break
            subprocess.run(['sleep', '1'])
        else:
            raise SystemExit(f'cannot remove {path}')


def write_root(path, data, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    os.chown(path, 0, 0)
    path.chmod(mode)


def add_user(dslocal, name, password, uid=501):
    """A local administrator as System Settings writes one: the user record and its admin and staff memberships."""
    salt, iterations = os.urandom(32), 50000
    entropy = hashlib.pbkdf2_hmac('sha512', password.encode(), salt, iterations, 128)
    shadow = plistlib.dumps({'SALTED-SHA512-PBKDF2': {'entropy': entropy, 'iterations': iterations, 'salt': salt}},
                            fmt=plistlib.FMT_BINARY)
    guid = str(uuid.uuid4()).upper()
    write_root(dslocal / 'users' / (name + '.plist'), plistlib.dumps({
        'name': [name], 'realname': [name], 'uid': [str(uid)], 'gid': ['20'], 'home': ['/Users/' + name], 'shell': ['/bin/zsh'],
        'generateduid': [guid], 'passwd': ['********'], 'authentication_authority': [';ShadowHash;HASHLIST:<SALTED-SHA512-PBKDF2>'],
        'ShadowHashData': [shadow], '_writers_passwd': [name], '_writers_realname': [name], '_writers_hint': [name]},
        fmt=plistlib.FMT_BINARY), 0o600)
    for group in ('admin', 'staff'):
        path = dslocal / 'groups' / (group + '.plist')
        record = plistlib.loads(path.read_bytes())
        record['users'] = [u for u in record.get('users', []) if u != name] + [name]
        record['groupmembers'] = [g for g in record.get('groupmembers', []) if g != guid] + [guid]
        write_root(path, plistlib.dumps(record, fmt=plistlib.FMT_BINARY), 0o600)


def add_home(template, mount, name, uid=501, gid=20):
    """The user's home as createhomedir makes it (the template's unlocalized part, then its English one), owned by the user, with
    .skipbuddy: Setup Assistant's MiniBuddy does not run for it."""
    home = mount / 'Users' / name
    home.mkdir(parents=True)
    for part in ('Non_localized', 'English.lproj'):
        source = template / USER_TEMPLATE / part
        if source.is_dir():
            subprocess.run(['ditto', source, home], check=True)
    (home / '.skipbuddy').touch()
    subprocess.run(['chown', '-R', f'{uid}:{gid}', home], check=True)
    home.chmod(0o750)
    # A home's own folders are the user's alone, as on an installed system; Public and its Drop Box follow the template's list.
    for private in ('Desktop', 'Documents', 'Downloads', 'Library', 'Movies', 'Music', 'Pictures'):
        if (home / private).is_dir():
            (home / private).chmod(0o700)
    # The template's own permission list (__permissions.plist): its CHMOD entries.
    permissions = template / USER_TEMPLATE / '__permissions.plist'
    for entry in plistlib.loads(permissions.read_bytes()) if permissions.is_file() else []:
        for path in entry.get('Paths', []) if entry.get('Command') == 'CHMOD' else []:
            target = home / path.lstrip('/')
            if target.exists():
                target.chmod(int(entry['Argument'], 8))


def add_keyboard_types(mount, entries):
    types = {}
    for entry in entries:
        key, _, value = entry.partition('=')
        if not value.isdigit() or len(key.split('-')) != 3 or not all(part.isdigit() for part in key.split('-')):
            raise SystemExit(f'--keyboard-type {entry}: expected PRODUCT-VENDOR-COUNTRY=TYPE in decimal')
        types[key] = int(value)
    write_root(mount / KEYBOARD_TYPE, plistlib.dumps({'keyboardtype': types}, fmt=plistlib.FMT_XML), 0o644)


def kcpassword(password):
    """/etc/kcpassword as loginwindow reads it: the password and its terminator, padded to 12-byte blocks, XORed with the cyclic key."""
    data = password.encode() + b'\0'
    data += bytes(-len(data) % 12)
    return bytes(b ^ KCPASSWORD_KEY[i % len(KCPASSWORD_KEY)] for i, b in enumerate(data))


def add_auto_login(mount, name, password):
    path = mount / LOGINWINDOW_PREFS
    prefs = plistlib.loads(path.read_bytes()) if path.is_file() else {}
    prefs['autoLoginUser'] = name
    write_root(path, plistlib.dumps(prefs, fmt=plistlib.FMT_BINARY), 0o644)
    write_root(mount / KCPASSWORD, kcpassword(password), 0o600)


def fletcher64(data):
    lo = hi = 0
    for (word,) in struct.iter_unpack('<I', data):
        lo = (lo + word) % 0xFFFFFFFF
        hi = (hi + lo) % 0xFFFFFFFF
    c0 = 0xFFFFFFFF - ((lo + hi) % 0xFFFFFFFF)
    c1 = 0xFFFFFFFF - ((lo + c0) % 0xFFFFFFFF)
    return struct.pack('<II', c0, c1)


def set_volume_uuid(raw, new):
    """Give the one volume of the raw container image the UUID new, in every checksummed superblock copy."""
    with open(raw, 'r+b') as f:
        data = bytearray(f.read())
    if data[32:36] != b'NXSB':
        raise SystemExit(f'{raw}: no APFS container superblock')
    size = struct.unpack_from('<I', data, 36)[0]
    found = set()
    for block in range(0, len(data) - size + 1, size):
        if data[block + 32:block + 36] != b'APSB' or fletcher64(data[block + 8:block + size]) != data[block:block + 8]:
            continue
        found.add(bytes(data[block + 240:block + 256]))
        data[block + 240:block + 256] = new.bytes
        data[block:block + 8] = fletcher64(data[block + 8:block + size])
    if len(found) != 1:
        raise SystemExit(f'{raw}: expected one volume, found {len(found)} volume UUIDs')
    with open(raw, 'r+b') as f:
        f.write(data)


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
            if args.user:
                add_user(scratch / DSLOCAL, *args.user.split(':', 1))
            link_template_directories(scratch)
            kept, linked = link_template_files(scratch)
            if args.skip_setup:   # after the links: Library/Managed Preferences is not kept as real files otherwise
                write_root(scratch / SETUP_SKIP, plistlib.dumps({'SkipSetupItems': SETUP_SKIP_ITEMS}, fmt=plistlib.FMT_XML), 0o644)
            if args.user:         # after the links, as real files ('Users/' is kept)
                add_home(template, scratch, args.user.split(':', 1)[0])
            if args.keyboard_type:
                add_keyboard_types(scratch, args.keyboard_type)
            if args.auto_login:
                add_auto_login(scratch, *args.user.split(':', 1))
            remove_volume_logs(scratch)
            with new_volume(raw, '512m') as mount:
                subprocess.run(['ditto', scratch, mount], check=True)
                remove_volume_logs(mount)
        (work / 'scratch.cdr').unlink()
        print(f'{kept} template files copied, {linked} linked to /{TEMPLATE}, '
              f'{len(READONLY)} directories linked', file=sys.stderr)
        if args.volume_uuid:
            set_volume_uuid(raw, args.volume_uuid)
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
