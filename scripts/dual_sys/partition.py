#!/usr/bin/env python3
"""Plan or apply a userdata/F2FS split through a rooted TWRP ADB connection."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import struct
import subprocess
import sys
import uuid

from gpt import GPT, read_gpt, require, size_bytes

HERE = Path(__file__).resolve().parent


class ADB:
    def __init__(self, executable, serial=None):
        self.executable = executable
        result = subprocess.run([executable, 'devices'], check=True, capture_output=True, text=True)
        rows = [line.split() for line in result.stdout.splitlines()[1:] if line.strip()]
        devices = [(r[0], r[1]) for r in rows if len(r) >= 2]
        if serial:
            require((serial, 'device') in devices or (serial, 'recovery') in devices,
                    'selected device is absent, offline or unauthorized')
        else:
            require(len(devices) == 1 and devices[0][1] in ('device', 'recovery'),
                    'connect exactly one authorized device, or use --serial')
            serial = devices[0][0]
        require(re.fullmatch(r'[A-Za-z0-9_.:-]+', serial), 'unsupported ADB serial')
        self.serial = serial

    def run(self, *args, **kwargs):
        return subprocess.run([self.executable, '-s', self.serial, *args], check=True, **kwargs)

    def shell(self, command):
        return self.run('shell', command, capture_output=True, text=True).stdout.strip()

    def read(self, path, sector, lba, count):
        result = self.run('exec-out', f'dd if={shlex.quote(path)} bs={sector} skip={lba} count={count} 2>/dev/null',
                          capture_output=True)
        require(len(result.stdout) == sector * count, f'short read from {path}')
        return result.stdout

    def push(self, local, remote):
        self.run('push', str(local), remote, stdout=subprocess.DEVNULL)


def block_path(value):
    require(re.fullmatch(r'/dev/block/[A-Za-z0-9_-]+', value), 'unsupported block-device path')
    return value


def identity(adb):
    require(adb.shell('id -u') == '0', 'ADB must already run as root in recovery')
    twrp = adb.shell('getprop ro.twrp.version')
    require(twrp and adb.shell('getprop sys.boot_completed') != '1', 'boot a compatible TWRP recovery first')
    serial = adb.shell('getprop ro.serialno') or adb.shell('getprop ro.boot.serialno')
    require(serial, 'recovery did not report a hardware serial')
    raw = block_path(adb.shell('readlink -f /dev/block/by-name/userdata'))
    node = Path(raw).name
    sys_path = adb.shell(f'readlink -f /sys/class/block/{node}')
    parent = Path(sys_path).parent.name
    require(re.fullmatch(r'[A-Za-z0-9_-]+', parent), 'cannot discover parent disk')
    disk = block_path('/dev/block/' + parent)
    index = int(adb.shell(f'cat /sys/class/block/{node}/partition'))
    sector = int(adb.shell(f'blockdev --getss {disk}'))
    total_bytes = int(adb.shell(f'blockdev --getsize64 {disk}'))
    require(sector in (512, 4096) and total_bytes > 0 and total_bytes % sector == 0,
            'unsupported disk geometry')
    return dict(adb_serial=adb.serial, hardware_serial=serial, model=adb.shell('getprop ro.product.model'),
                device=adb.shell('getprop ro.product.device'), kernel=adb.shell('uname -r'),
                machine=adb.shell('uname -m'), twrp=twrp,
                raw=raw, disk=disk, index=index, sector=sector, total_bytes=total_bytes)


def snapshot(adb, info):
    return read_gpt(lambda lba, count: adb.read(info['disk'], info['sector'], lba, count),
                    info['sector'], info['total_bytes'] // info['sector'])


def expected_blocks(before, limit):
    if before <= limit:
        return before
    request = (limit - before % 512) // 512 * 512
    require(request > 0, 'userdata target too small')
    return request + before % 512


def show(info, gpt):
    print(f"Device: {info['model']} ({info['device']}), ADB {info['adb_serial']}")
    print(f"TWRP: {info['twrp']}; kernel: {info['kernel']}; architecture: {info['machine']}")
    print(f"Disk: {info['disk']}; logical sector: {info['sector']} bytes")
    print('Index  Name                        First LBA       Last LBA        GiB')
    for e in gpt.entries:
        gib = (e['end'] - e['start'] + 1) * info['sector'] / (1 << 30)
        print(f"{e['index']:5}  {e['name']:24} {e['start']:13} {e['end']:14} {gib:10.3f}")


def prepare(adb, args, info, gpt):
    require(args.helper and args.output and args.size_gib, 'plan/apply requires --helper, --output and --size-gib')
    helper = Path(args.helper).resolve()
    require(helper.is_file(), 'compiled f2fs-shrink helper not found')
    elf = helper.read_bytes()[:20]
    machine = {'aarch64': 183, 'armv7l': 40, 'armv8l': 40, 'x86_64': 62}.get(info['machine'])
    require(len(elf) == 20 and elf[:4] == b'\x7fELF' and elf[5] == 1 and
            struct.unpack_from('<H', elf, 18)[0] == machine, 'helper ELF architecture does not match the phone')
    primary, backup, layout = gpt.split(size_bytes(args.size_gib), info['index'])
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    os.chmod(output, 0o700)
    remote = '/tmp/unixnu-dual-' + uuid.uuid4().hex
    adb.shell(f'mkdir -m 700 {remote}')
    adb.push(helper, remote + '/f2fs-shrink')
    adb.shell(f'chmod 700 {remote}/f2fs-shrink')
    fs = json.loads(adb.shell(f'{remote}/f2fs-shrink probe {info["raw"]}'))
    block_path(fs['mapped'])
    require(fs['partition_bytes'] == layout['old_userdata_bytes'], 'kernel userdata size differs from GPT')
    start = int(adb.shell(f'cat /sys/class/block/{Path(info["raw"]).name}/start')) * 512
    require(start == layout['userdata_start'] * info['sector'], 'kernel userdata start differs from GPT')
    limit = layout['new_userdata_bytes'] // 4096
    before = fs['blocks']
    after = expected_blocks(before, limit)
    require(before > 0 and before * 4096 <= layout['old_userdata_bytes'], 'invalid F2FS size')
    if before > limit:
        request = after - before % 512
        require(before - request < fs['available_blocks'], 'not enough available F2FS space')
    variables = dict(DISK=info['disk'], RAW=info['raw'], MAPPED=fs['mapped'],
                     HARDWARE_SERIAL=info['hardware_serial'], KERNEL=info['kernel'],
                     DISK_BYTES=info['total_bytes'], SECTOR=info['sector'],
                     BACKUP_LBA=gpt.total - 1 - gpt.h['blocks'],
                     PRIMARY_BLOCKS=2 + gpt.h['blocks'], BACKUP_BLOCKS=1 + gpt.h['blocks'],
                     OLD_BYTES=layout['old_userdata_bytes'], OLD_BLOCKS=before,
                     EXPECTED_BLOCKS=after, LIMIT_BLOCKS=limit,
                     USER_START_512=start // 512,
                     CONFIRM=f"{adb.serial} unixnu {layout['unixnu_bytes']}")
    for name, data in (('gpt-primary.before', gpt.primary), ('gpt-backup.before', gpt.backup),
                       ('gpt-primary.after', primary), ('gpt-backup.after', backup)):
        (output / name).write_bytes(data)
    shutil.copyfile(helper, output / 'f2fs-shrink')
    shutil.copyfile(HERE / 'twrp.sh', output / 'twrp.sh')
    (output / 'plan.env').write_text(''.join(f'{k}={shlex.quote(str(v))}\n' for k, v in variables.items()),
                                   encoding='utf-8', newline='\n')
    plan = dict(identity=info, filesystem=fs, layout=layout, remote=remote,
                expected_blocks=after, limit_blocks=limit)
    (output / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8', newline='\n')
    files = sorted(p for p in output.iterdir() if p.is_file())
    (output / 'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files),
                                    encoding='utf-8', newline='\n')
    for path in [*files, output / 'SHA256SUMS']:
        adb.push(path, remote + '/' + path.name)
    adb.shell(f'chmod 700 {remote}/f2fs-shrink')
    print(f"\nPlanned unixnu: {layout['unixnu_bytes'] / (1 << 30):.6f} GiB, "
          f"LBA {layout['unixnu_start']}..{layout['unixnu_end']}")
    print(f"Remaining userdata: {layout['new_userdata_bytes'] / (1 << 30):.6f} GiB")
    print(f"Alignment gap after unixnu: {layout['tail_gap_bytes']} bytes")
    print(f'F2FS blocks: {before} -> {after}; partition limit: {limit}')
    print(f'Host bundle and original GPT: {output}\nRecovery bundle: {remote}')
    adb.run('shell', f'sh {remote}/twrp.sh check')
    if args.command == 'plan':
        print('Plan only. No filesystem or partition-table writes performed.')
        return
    print('This changes the filesystem and GPT. Review the device and partition size before continuing.')
    confirmation = input(f"Type exactly: {variables['CONFIRM']}\n> ")
    require(confirmation == variables['CONFIRM'], 'confirmation did not match; nothing resized')
    # No timeout/retry: the kernel may take a long time to move allocated sections.
    with (output / 'apply.log').open('w') as log:
        process = subprocess.Popen([adb.executable, '-s', adb.serial, 'shell',
                                    f'sh {remote}/twrp.sh apply {shlex.quote(confirmation)}'],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end='', flush=True)
            log.write(line)
            log.flush()
        require(process.wait() == 0, 'recovery stopped; keep this bundle and inspect apply.log before rebooting or retrying')
    current = snapshot(adb, info)
    require(current.primary == primary and current.backup == backup, 'post-write GPT readback mismatch; do not reboot')
    print('GPT readback passed. Reboot into recovery, decrypt /data and run verify --plan on this bundle.')


def verify(adb, args, info, gpt):
    require(args.plan, 'verify requires --plan /path/to/plan.json')
    plan = json.loads(Path(args.plan).read_text(encoding='utf-8'))
    saved = plan['identity']
    require(all(info[k] == saved[k] for k in ('hardware_serial', 'disk', 'raw', 'sector', 'total_bytes')),
            'device does not match the saved plan')
    root = Path(args.plan).resolve().parent
    require(gpt.primary == (root / 'gpt-primary.after').read_bytes() and
            gpt.backup == (root / 'gpt-backup.after').read_bytes(), 'GPT differs from the completed plan')
    layout = plan['layout']
    unixnu = block_path(adb.shell('readlink -f /dev/block/by-name/unixnu'))
    for path, start, size in ((info['raw'], layout['userdata_start'], layout['new_userdata_bytes']),
                              (unixnu, layout['unixnu_start'], layout['unixnu_bytes'])):
        node = Path(path).name
        require(int(adb.shell(f'blockdev --getsize64 {path}')) == size and
                int(adb.shell(f'cat /sys/class/block/{node}/start')) * 512 == start * info['sector'],
                'kernel partition view is stale or incorrect; reboot into recovery')
        sys_path = adb.shell(f'readlink -f /sys/class/block/{node}')
        require(Path(sys_path).parent.name == Path(info['disk']).name, 'partition is on another disk')
    remote = '/tmp/unixnu-verify-' + uuid.uuid4().hex
    adb.push(root / 'f2fs-shrink', remote)
    adb.shell(f'chmod 700 {remote}')
    fs = json.loads(adb.shell(f'{remote} probe {info["raw"]}'))
    require(fs['blocks'] == plan['expected_blocks'] and fs['blocks'] <= plan['limit_blocks'], 'unexpected F2FS size')
    print('PASS: GPT copies, kernel partition ranges and mounted F2FS size match the plan.')
    print('Check Android boot and your files separately; no filesystem was created in unixnu.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('inspect', 'plan', 'apply', 'verify'))
    parser.add_argument('--adb', default='adb', help='ADB executable, including adb.exe on Windows')
    parser.add_argument('--serial', help='required when multiple ADB devices are connected')
    parser.add_argument('--size-gib', help='new unixnu capacity in GiB; whole MiB increments')
    parser.add_argument('--helper', help='statically linked f2fs-shrink executable for the phone ABI')
    parser.add_argument('--output', help='new host directory for the plan, GPT backup and recovery bundle')
    parser.add_argument('--plan', help='plan.json from a completed apply, for verify')
    args = parser.parse_args()
    try:
        adb = ADB(args.adb, args.serial)
        info = identity(adb)
        gpt = snapshot(adb, info)
        show(info, gpt)
        if args.command in ('plan', 'apply'):
            prepare(adb, args, info, gpt)
        elif args.command == 'verify':
            verify(adb, args, info, gpt)
    except (ValueError, OSError, subprocess.CalledProcessError, EOFError, KeyError) as exc:
        print(f'STOP: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
