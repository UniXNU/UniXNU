#!/usr/bin/env python3
"""Create a fresh macOS APFS volume group with native macOS tools.

hdiutil exposes the container window of the SHNGDATA store. diskutil creates
the role volumes; APFS.framework links the restored System and Data. System
filesystem metadata is retained byte-for-byte before native container growth.
ditto installs SystemOS, AppOS and the complete Data template.
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import tempfile
import tomllib

from macos_container import PAGE, empty_seed, seed_digest, header, mark_data, install_addon, mark_empty_xart
from macos_apfs import APFS
from macos_accounts import (add_user, add_home, add_auto_login, add_keyboard_types, write_root,
                            DSLOCAL, SETUP_SKIP, SETUP_SKIP_ITEMS)

ROLES = {'System': 'S', 'Data': 'D', 'Preboot': 'B', 'VM': 'V', 'Update': 'E', 'Hardware': 'H', 'xART': 'X'}
CONTAINER_HINT = 'EF57347C-0000-11AA-AA11-00306543ECAC'
APPLE_TOOLS = ('sbin/fsck', 'sbin/mount', 'System/Library/Filesystems/apfs.fs/Contents/Resources/apfs_boot_util')


def run(*command, capture=False):
    result = subprocess.run(list(map(str, command)), check=True, stdout=subprocess.PIPE if capture else None)
    return result.stdout if capture else None


def plist(*command):
    return plistlib.loads(run(*command, capture=True))


def container_info(device):
    containers = plist('diskutil', 'apfs', 'list', '-plist', device)['Containers']
    if len(containers) != 1:
        raise ValueError('expected exactly one APFS container')
    return containers[0]


def volume(info, role):
    found = [v for v in info['Volumes'] if [str(r).lower() for r in v.get('Roles', [])] == [role.lower()]]
    if len(found) != 1:
        raise ValueError(f'expected exactly one {role} volume')
    return found[0]


@contextlib.contextmanager
def attached(image, offset=0, size=None, readonly=False):
    command = ['hdiutil', 'attach', '-nomount', '-nobrowse', '-noautoopen', '-owners', 'on', '-plist']
    if readonly:
        command.append('-readonly')
    if size is not None:
        command += ['-imagekey', 'diskimage-class=CRawDiskImage', '-section', f'{offset // 512},{size // 512}']
    result = plist(*command, image)
    entries = result['system-entities']
    whole = entries[0]['dev-entry']
    try:
        yield whole, entries
    finally:
        run('hdiutil', 'detach', whole)


@contextlib.contextmanager
def mounted(device, point, readonly=False):
    point.mkdir(parents=True, exist_ok=True)
    command = ['diskutil', 'mount'] + (['readOnly'] if readonly else [])
    run(*command, '-mountPoint', point, device)
    changed_ownership = False
    try:
        info = plist('diskutil', 'info', '-plist', device)
        if not info.get('GlobalPermissionsEnabled'):
            run('diskutil', 'enableOwnership', device)
            changed_ownership = True
            info = plist('diskutil', 'info', '-plist', device)
        if not info.get('GlobalPermissionsEnabled'):
            raise ValueError('volume ownership must be enabled')
        if Path(info['MountPoint']).resolve() != point.resolve():
            raise ValueError('unexpected volume mount point')
        yield point
    finally:
        if changed_ownership:
            run('diskutil', 'disableOwnership', device)
        run('diskutil', 'unmount', device)


@contextlib.contextmanager
def source_mount(image, scratch, name):
    # A private clone avoids changing an existing attachment's ownership or mount options.
    clone = scratch / f'{name}.dmg'
    run('/bin/cp', '-c', image, clone)
    try:
        with attached(clone, readonly=True) as (whole, entries):
            disks = [e['dev-entry'] for e in entries if e.get('volume-kind') == 'apfs']
            if len(disks) != 1:
                raise ValueError(f'{image}: expected one APFS source volume')
            with mounted(disks[0], scratch / name, readonly=True) as point:
                yield point, disks[0], whole
    finally:
        clone.unlink(missing_ok=True)


def copy_tree(source, target):
    # Cryptex paths replace the IPSW's links into Preboot with real contents.
    # Walk top-down so no destination parent link can lead outside this volume.
    for directory, names, files in os.walk(source, followlinks=False):
        for name in [*names, *files]:
            destination = target / (Path(directory) / name).relative_to(source)
            if destination.is_symlink():
                destination.unlink()
    result = subprocess.run(['ditto', '--hfsCompression', '--rsrc', '--extattr', '--acl', source, target],
                            text=True, stderr=subprocess.PIPE)
    restricted = 0
    for line in result.stderr.splitlines():
        prefix, separator, reason = line.rpartition(': ')
        destination = Path(prefix.removeprefix('ditto: '))
        try:
            original = source / destination.relative_to(target)
        except ValueError:
            original = None
        if (not separator or reason != 'Operation not permitted' or original is None or
                not os.lstat(original).st_flags & 0x00080000 or not destination.exists()):
            raise ValueError(f'ditto failed: {result.stderr.strip()}')
        if original.is_file() and digest(original) != digest(destination):
            raise ValueError(f'incomplete restricted file copy: {original}')
        restricted += 1
    if result.returncode and not restricted:
        raise ValueError(f'ditto failed ({result.returncode})')
    if restricted:
        print(f'Copied {restricted} entries without the host-restricted flag', flush=True)


def preboot_dirs(base):
    (base / 'Cryptexes').mkdir(parents=True, exist_ok=True)
    (base / 'com.apple.security.cryptexd/Cryptexes').mkdir(parents=True, exist_ok=True)
    link = base / 'Cryptexes/OS'
    link.symlink_to('/')


def add_volume(container, name, role, sibling=None):
    command = ['diskutil', 'apfs', 'addVolume', container, 'APFS', name, '-role', role, '-nomount']
    if sibling:
        command += ['-groupWith', sibling]
    run(*command)
    return volume(container_info(container), name)['DeviceIdentifier']


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        while block := handle.read(8 << 20):
            result.update(block)
    return result.hexdigest()


def verify_group(container):
    groups = plist('diskutil', 'apfs', 'listVolumeGroups', '-plist', container)['Containers'][0]['VolumeGroups']
    matched = [g for g in groups if {v.get('Role') for v in g.get('Volumes', [])} == {'System', 'Data'}]
    if len(matched) != 1:
        raise ValueError('System and Data must belong to exactly one native volume group')
    return matched[0]


def build(args):
    logical = args.size_gib << 30
    pages = logical // PAGE
    offset = (1 + (pages + PAGE * 8 - 1) // (PAGE * 8)) * PAGE
    board = tomllib.loads((args.device / 'board.toml').read_text())['userdata']
    capacity = (board['last_lba'] - board['first_lba'] + 1) * board.get('lba_bytes', 4096)
    reserve = args.log_reserve_mib << 20
    base = capacity - reserve - offset - logical
    if base < 4096 + 1024 * 4096 or base % PAGE:
        raise ValueError('container does not fit below the userdata log reserve')
    args.output.mkdir(parents=True)
    store = args.output / 'data-store.img'
    with store.open('xb') as handle:
        handle.truncate(capacity - reserve)
        handle.seek(base)
        handle.write(header(pages, seed_digest(logical)))
    verification = {'tools': {}, 'ownership': {}, 'firmlinks': {}}
    with tempfile.TemporaryDirectory(prefix='native-apfs-', dir=args.output) as td:
        scratch = Path(td)
        with source_mount(args.os_image, scratch, 'os') as (source, source_device, source_whole):
            source_uuid = plist('diskutil', 'info', '-plist', source_device)['VolumeUUID']
            if args.source_uuid and source_uuid.upper() != args.source_uuid.upper():
                raise ValueError('IPSW System UUID does not match --source-uuid')
            source_container = plist('diskutil', 'info', '-plist', source_device)['APFSContainerReference']
            source_info = container_info(source_container)
            if len(source_info['PhysicalStores']) != 1 or len(source_info['Volumes']) != 1:
                raise ValueError('IPSW input must contain only System on one physical store')
            source_store = '/dev/' + source_info['PhysicalStores'][0]['DeviceIdentifier']
            source_size = source_info['PhysicalStores'][0]['Size']
            if source_size > logical:
                raise ValueError('IPSW System container is larger than the target')
            with open(source_store.replace('/dev/disk', '/dev/rdisk'), 'rb', buffering=0) as original, store.open('r+b') as output:
                done = 0
                while done < source_size:
                    block = original.read(min(8 << 20, source_size - done))
                    if not block:
                        raise ValueError('short IPSW container read')
                    if any(block):
                        output.seek(base + offset + done)
                        output.write(block)
                    done += len(block)
            source_tools = {name: digest(source / name) for name in APPLE_TOOLS}
            firmlinks = (source / 'usr/share/firmlinks').read_bytes()
            with attached(store, base + offset, logical) as (whole, entries):
                container = next(e['dev-entry'] for e in entries if e.get('content-hint') == CONTAINER_HINT)
                info = container_info(container)
                if [p['DeviceIdentifier'] for p in info['PhysicalStores']] != [whole.removeprefix('/dev/')]:
                    raise ValueError('container physical store does not match the new image')
                if len(info['Volumes']) != 1:
                    raise ValueError('IPSW input must contain only System')
                run('diskutil', 'apfs', 'resizeContainer', container, '0')
                system_dev = volume(container_info(container), 'System')['DeviceIdentifier']
                data_dev = add_volume(container, 'Data', 'D')
                APFS().group(container, [system_dev, data_dev])
                verify_group(container)
                for role in ('Preboot', 'VM', 'Update', 'Hardware'):
                    add_volume(container, role, ROLES[role])
                run('diskutil', 'apfs', 'addVolume', container, 'APFS', 'xART', '-nomount')
                pending_xart = next(v for v in container_info(container)['Volumes'] if v['Name'] == 'xART')
                run('diskutil', 'unmountDisk', container)
                with mounted(system_dev, scratch / 'system') as target:
                    with source_mount(args.systemos, scratch, 'systemos') as (cryptex, _, _):
                        copy_tree(cryptex, target)
                    preboot_dirs(target / 'System/Volumes/Preboot')
                    install_addon(args.addon, target, system=True)
                    if (target / 'usr/share/firmlinks').read_bytes() != firmlinks:
                        raise ValueError('System firmlink manifest changed')
                    for name, expected in source_tools.items():
                        actual = digest(target / name)
                        if actual != expected:
                            raise ValueError(f'original Apple tool changed: {name}')
                        verification['tools'][name] = actual
                    verification['firmlinks']['manifest_sha256'] = hashlib.sha256(firmlinks).hexdigest()
                    for line in firmlinks.decode().splitlines():
                        if not line or line.startswith('#'):
                            continue
                        relative = line.split()[0].lstrip('/')
                        if not os.path.lexists(source / relative):
                            if os.path.lexists(target / relative):
                                raise ValueError(f'unexpected firmlink source: {relative}')
                            verification['firmlinks'][relative] = None
                            continue
                        before, after = (source / relative).lstat(), (target / relative).lstat()
                        if before.st_flags & 0x00800000 and not after.st_flags & 0x00800000:
                            raise ValueError(f'native firmlink metadata missing: {relative}')
                        verification['firmlinks'][relative] = bool(after.st_flags & 0x00800000)
                with mounted(data_dev, scratch / 'data') as target:
                    template = source / 'System/Library/Templates/Data'
                    copy_tree(template, target)
                    for directory in ('tmp', 'log', 'run', 'vm', 'folders', 'db/dslocal/nodes/Default'):
                        (target / 'private/var' / directory).mkdir(parents=True, exist_ok=True)
                    (target / 'private/tmp').mkdir(parents=True, exist_ok=True)
                    for path in ('private/tmp', 'private/var/tmp'):
                        (target / path).chmod(0o1777)
                    install_addon(args.addon, target, system=False)
                    if args.skip_setup:
                        write_root(target / 'private/var/db/.AppleSetupDone', b'', 0o644)
                        write_root(target / SETUP_SKIP, plistlib.dumps({'SkipSetupItems': SETUP_SKIP_ITEMS}), 0o644)
                    if args.user:
                        name, password = args.user.split(':', 1)
                        add_user(target / DSLOCAL, name, password)
                        add_home(template, target, name)
                        if args.auto_login:
                            add_auto_login(target, name, password)
                    if args.keyboard_type:
                        add_keyboard_types(target, args.keyboard_type)
                    checked = non_root = 0
                    for directory, names, files in os.walk(template):
                        for name in [*names, *files]:
                            original = Path(directory) / name
                            relative = original.relative_to(template)
                            before, after = original.lstat(), (target / relative).lstat()
                            if (before.st_uid, before.st_gid) != (after.st_uid, after.st_gid):
                                raise ValueError(f'Data template ownership changed: {relative}')
                            checked += 1
                            non_root += before.st_uid != 0
                    verification['ownership'] = {'entries_checked': checked, 'non_root_owned_entries': non_root}
                preboot_dev = volume(container_info(container), 'Preboot')['DeviceIdentifier']
                with mounted(preboot_dev, scratch / 'preboot') as target:
                    preboot_dirs(target)
                    with source_mount(args.appos, scratch, 'appos') as (app, _, _):
                        copy_tree(app, target / 'Cryptexes/App')
                (args.output / 'native-content-verification.json').write_text(json.dumps(verification, indent=2) + '\n')
                info = container_info(container)
                roles = {role.lower(): {'uuid': volume(info, role)['APFSVolumeUUID'],
                                       'index': int(volume(info, role)['DeviceIdentifier'].split('s')[-1]) - 1}
                         for role in ROLES if role != 'xART'}
                roles['xart'] = {'uuid': pending_xart['APFSVolumeUUID'], 'index': int(pending_xart['DeviceIdentifier'].split('s')[-1]) - 1}
                if len(info['Volumes']) != len(ROLES):
                    raise ValueError('unexpected extra APFS volumes')
                if info['CapacityCeiling'] != logical:
                    raise ValueError('APFS container size differs from the configured size')
                run('diskutil', 'unmountDisk', container)
    verification['xart_superblocks'] = mark_empty_xart(store, base + offset, logical, roles['xart']['uuid'])
    with attached(store, base + offset, logical) as (whole, entries):
        container = next(e['dev-entry'] for e in entries if e.get('content-hint') == CONTAINER_HINT)
        info = container_info(container)
        if len(info['Volumes']) != len(ROLES):
            raise ValueError('unexpected extra APFS volumes')
        for role in ROLES:
            if volume(info, role)['APFSVolumeUUID'] != roles[role.lower()]['uuid']:
                raise ValueError(f'volume role or identity mismatch: {role}')
        verification['volume_group'] = verify_group(container)
        with tempfile.TemporaryDirectory(prefix='verify-apfs-', dir=args.output) as td:
            for role in ROLES:
                with mounted(volume(info, role)['DeviceIdentifier'], Path(td) / role, readonly=True):
                    pass
        verification['mounted_roles'] = list(ROLES)
        run('diskutil', 'unmountDisk', container)
        check = subprocess.run(['fsck_apfs', '-n', whole.replace('/dev/disk', '/dev/rdisk')],
                               text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (args.output / 'fsck-apfs.log').write_text(check.stdout)
        if check.returncode:
            raise ValueError(f'fsck_apfs failed ({check.returncode})')
        verification['fsck_apfs_exit'] = check.returncode
    present = mark_data(store, base + offset, logical, store_offset=base)
    (args.output / 'scratch-data.img').write_bytes(empty_seed(logical))
    layout = dict(format='UniXNU.NativeAPFS.v1', bytes=logical, source_system_uuid=source_uuid,
                  store=store.name, seed='scratch-data.img', window_offset=offset, store_offset=base,
                  userdata_bytes=capacity, log_reserve_bytes=reserve, **roles)
    (args.output / 'disk.json').write_text(json.dumps(layout, indent=2) + '\n')
    verification['present_pages'] = present
    (args.output / 'verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    if 'SUDO_UID' in os.environ and 'SUDO_GID' in os.environ:
        for path in [*args.output.iterdir(), args.output]:
            os.chown(path, int(os.environ['SUDO_UID']), int(os.environ['SUDO_GID']))
    print(f'{store}: {present} stored pages; System UUID {roles["system"]["uuid"]}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--os-image', '--os-raw', dest='os_image', required=True, type=Path)
    parser.add_argument('--systemos', required=True, type=Path)
    parser.add_argument('--appos', required=True, type=Path)
    parser.add_argument('--source-uuid', help='Expected IPSW System UUID')
    parser.add_argument('--addon', required=True, type=Path)
    parser.add_argument('--device', required=True, type=Path, help='Device repository with userdata geometry')
    parser.add_argument('--log-reserve-mib', type=int, default=1024)
    parser.add_argument('--size-gib', type=int, default=210)
    parser.add_argument('--skip-setup', action='store_true')
    parser.add_argument('--user', help='NAME:PASSWORD for a local administrator')
    parser.add_argument('--auto-login', action='store_true')
    parser.add_argument('--keyboard-type', action='append', default=[])
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if sys.platform != 'darwin' or os.geteuid() != 0:
        parser.error('run as root on macOS to preserve numeric ownership and APFS metadata')
    if not 3 <= args.size_gib <= 1024:
        parser.error('--size-gib must be in 3..1024')
    if args.output.exists():
        parser.error('output directory must be new')
    if args.user and (':' not in args.user or not re.fullmatch(r'[a-z_][a-z0-9_-]*', args.user.split(':', 1)[0])):
        parser.error('--user requires NAME:PASSWORD with a valid local account name')
    if args.auto_login and not args.user:
        parser.error('--auto-login requires --user')
    for name in ('os_image', 'systemos', 'appos', 'addon'):
        value = getattr(args, name).resolve()
        if not value.is_file():
            parser.error(f'input not found: {value}')
        setattr(args, name, value)
    args.output = args.output.resolve()
    build(args)


if __name__ == '__main__':
    main()
