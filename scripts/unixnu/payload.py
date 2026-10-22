"""Boot payload: the FAT volume that becomes the ramdisk of the boot image.

The volume is what UniXNU reads at boot: its config, the kernel Mach-O (optionally with the panic
screen patched into a copy), the device tree sidecar the board script generates, and optionally the
trust cache and the Data ramdisk seed. The loader (DarwinBoot) is part of the firmware volume.

Inputs that are not in a repository are options: the prelinked kernel (default: the output of
"build kernel"), --trust-cache, --data-ramdisk and the platform seed --unique-chip-id.
The volume is written with mtools, without mounting, so it is the same on every run.
"""
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from .util import Error, expand, log, run, sha256_file, tool

EPOCH = 315532800   # 1980-01-01, the first FAT timestamp; keeps the volume reproducible


def paths(ctx):
    out = ctx.work / 'payload'
    return out, out / 'payload.img', out / 'payload.json'


def check_args(arguments):
    for value in arguments:
        if not re.fullmatch(r'[A-Za-z0-9_.\-]+(=[A-Za-z0-9_.,\-]+)?', value):
            raise Error(f'unsupported kernel argument: {value}')
    line = ' '.join(arguments)
    # DarwinBoot copies the command line into a 1024-byte buffer and refuses a longer one.
    if len(line) > 1000:
        raise Error(f'the kernel command line is {len(line)} bytes; the limit is 1000')
    return line


def check_native_root(kernel, arguments):
    """Refuse the known bare-metal AMFI panic before the volume is written."""
    values = {}
    for argument in arguments:
        key, separator, value = argument.partition('=')
        if separator:
            values.setdefault(key, []).append(value)
    if '1' not in values.get('native-ufs-root', []):
        return
    if values.get('sheng-pmgr') != ['2']:
        raise Error('native UFS root boot needs exactly one sheng-pmgr=2; the unchanged target AMFI otherwise panics with No PMGR')
    symbols = run([tool('llvm-nm', 'brew install llvm'), '--defined-only', kernel], capture=True)
    if not any(line.split()[-1:] == ['_sheng_pmgr_run'] for line in symbols.splitlines()):
        raise Error('the native UFS root kernel lacks the linked sheng PMGR integration')


def write_volume(stage, image, label, size_mib):
    for tool_name in ('mformat', 'mcopy'):
        tool(tool_name, 'brew install mtools')
    image.unlink(missing_ok=True)
    env = dict(os.environ, MTOOLS_SKIP_CHECK='1', TZ='UTC')
    sectors = size_mib * 2048
    run(['mformat', '-C', '-F', '-T', str(sectors), '-v', label, '-N', '53484e47', '-i', image, '::'], env=env, capture=True)
    for entry in sorted(stage.iterdir()):
        run(['mcopy', '-i', image, '-s', '-Q', '-m', entry, '::/'], env=env, capture=True)


def skip_setup_seed(ctx, base, tool_path, tool_args=()):
    """A copy of the Data seed whose preferences mark Setup (the Hello pages) as done; cached by the hash of the base and the
    tool's extra arguments (board.toml [payload] skip_setup_args)."""
    tool('hdiutil')
    out = paths(ctx)[0]
    out.mkdir(parents=True, exist_ok=True)
    key = sha256_file(base)[:12] + (('-' + hashlib.sha256(' '.join(tool_args).encode()).hexdigest()[:8]) if tool_args else '')
    seed = out / f'data-skip-setup-{key}.dbr'
    if not seed.is_file():
        log('payload: marking Setup as done in a copy of the Data seed (mounts the seed read-write, no root needed)')
        for stale in out.glob('data-skip-setup-*'):
            stale.unlink()
        (ctx.tree / 'build').mkdir(exist_ok=True)
        run(['python3', ctx.tree / tool_path, base, seed, *tool_args], cwd=ctx.tree, log_file=ctx.logs / 'payload-skip-setup.log')
    return seed


def build(ctx, kernel=None):
    log('payload')
    spec = ctx.board.get('payload')
    if not spec:
        raise Error('board.toml has no [payload]')
    args = ctx.args
    kernel = expand(kernel or getattr(args, 'kernel', None) or ctx.work / 'kernel/kernel.macho')
    if not kernel.is_file():
        raise Error(f'kernel not found: {kernel}; run "unixnu build kernel" or pass --kernel FILE')
    extra = list(getattr(args, 'kernel_arg', None) or [])
    # An extra NAME=VALUE replaces the board's argument of the same name.
    names = {item.split('=', 1)[0] for item in extra}
    arguments = [item for item in spec.get('kernel_args', []) if item.split('=', 1)[0] not in names] + extra
    line = check_args(arguments)
    check_native_root(kernel, arguments)
    owner_trust = getattr(args, 'owner_trust_cache', None)
    trust = expand(owner_trust or args.trust_cache) if (owner_trust or getattr(args, 'trust_cache', None)) else None
    if trust:
        allowed = spec.get('trust_cache_sha256')
        if not trust.is_file():
            raise Error(f'trust cache not found: {trust}')
        if allowed and not owner_trust and sha256_file(trust) not in allowed:
            raise Error(f'{trust} is not one of the trust caches this board accepts (board.toml [payload] trust_cache_sha256)')
    data = expand(args.data_ramdisk) if getattr(args, 'data_ramdisk', None) else None
    if data and not data.is_file():
        raise Error(f'Data ramdisk not found: {data}')
    if getattr(args, 'skip_setup', False):
        if not data:
            raise Error('--skip-setup edits the Data seed: pass the original one with --data-ramdisk FILE')
        if not spec.get('skip_setup_tool'):
            raise Error('board.toml [payload] has no skip_setup_tool')
        data = skip_setup_seed(ctx, data, spec['skip_setup_tool'], [str(arg) for arg in spec.get('skip_setup_args', [])])
    addon = expand(args.gpu_addon) if getattr(args, 'gpu_addon', None) else None
    if addon and (not addon.is_file() or addon.read_bytes()[:8] != b'NGPUADD2'):
        raise Error(f'GPU addon not found or not made by scripts/make-gpu-addon.py: {addon}')
    seed = getattr(args, 'unique_chip_id', None) or os.environ.get('UNIXNU_UNIQUE_CHIP_ID')
    adt = spec.get('adt', {})
    if adt.get('unique_chip_id') == 'required' and not seed:
        raise Error('the platform seed is not stored in any repository: pass --unique-chip-id HEX (or UNIXNU_UNIQUE_CHIP_ID)')
    out, image, report = paths(ctx)
    stage = out / 'stage'
    shutil.rmtree(stage, ignore_errors=True)
    payloads = stage / 'EFI/UniXNU/Payloads'
    payloads.mkdir(parents=True)
    shutil.copyfile(kernel, payloads / 'kernel.macho')
    # The entry probe (stage bars, optional reset) is wanted with either setting; the panic screen is only one part of it.
    if spec.get('panic_screen') or spec.get('entry_probe_reset_delay'):
        probe = (['--reset-delay', str(int(spec['entry_probe_reset_delay']))]
                 if spec.get('entry_probe_reset_delay') else ['--no-reset'])
        screen = ['--panic-screen'] if spec.get('panic_screen') else []
        if spec.get('entry_probe_reset_delay') and spec.get('entry_probe_reset_after'):
            # Stage 4 in place of stage 3: reset after the Nth call to SYMBOL in FUNCTION.
            probe += ['--reset-after', spec['entry_probe_reset_after'], '--in', spec.get('entry_probe_reset_in', '_arm_init'),
                      '--occurrence', str(int(spec.get('entry_probe_reset_occurrence', 1)))]
            if spec.get('entry_probe_reset_before'):
                # At the call site, without making the call (and without the delay).
                probe.append('--reset-before')
        run(['python3', ctx.tree / 'scripts/patch-xnu-entry-probe.py', payloads / 'kernel.macho', *screen, *probe],
            cwd=ctx.tree, env=dict(os.environ, UNIXNU_UEFI=str(ctx.uefi or '')), log_file=ctx.logs / 'payload-patch.log')
    if trust:
        shutil.copyfile(trust, payloads / 'kernel.macho.trustcache')
    if addon:
        shutil.copyfile(addon, payloads / 'kernel.macho.gpuaddon')
    if data:
        shutil.copyfile(data, payloads / 'scratch-data.img')
    command = ['python3', ctx.tree / adt['tool'], '--output', payloads / 'kernel.macho.adt', '--dram-size', str(spec['dram_size'])]
    for key, flag in (('owned_memory_size', '--owned-memory-size'), ('root_match_volume_uuid', '--root-match-volume-uuid'),
                      ('chip_id', '--chip-id'), ('cpu_regs', '--cpu-regs'), ('psci_method', '--psci-method')):
        if adt.get(key) is not None:
            command += [flag, str(adt[key])]
    if seed:
        command += ['--unique-chip-id', seed]
    if data:
        command.append('--packed-data-ramdisk' if adt.get('packed_data_ramdisk') else '--data-ramdisk')
    if trust:
        command.append('--trust-cache')
    if addon:
        command.append('--gpu-addon')
    if adt.get('ipad_identity'):
        command.append('--ipad-identity')
    if data and adt.get('persistent_data'):
        command.append('--persistent-data')
    # Fixups of signed text (patches/xnu/native-text-fixup.patch) travel in /chosen/text-fixups, outside the 1000-byte command line.
    for fixup in spec.get('text_fixups', []):
        if not re.fullmatch(r'[A-Za-z0-9_.\-]{1,63},[0-9a-fA-F]{1,16},(?:[0-9a-fA-F]{2}){1,16},(?:[0-9a-fA-F]{2}){1,16}', fixup) or len(fixup) >= 160:
            raise Error(f'malformed text fixup in board.toml [payload] text_fixups: {fixup}')
        command += ['--text-fixup', fixup]
    run(command, cwd=ctx.tree, env=dict(os.environ, UNIXNU_UEFI=str(ctx.uefi or '')), log_file=ctx.logs / 'payload-adt.log')
    initrd = 'initrd = "Payloads/scratch-data.img"\n' if data else ''
    loader = '' if spec.get('loader', 'firmware') == 'firmware' else '[[driver]]\npath = "Payloads/DarwinBoot.efi"\n'
    config = (f'version = 1\n[boot]\ntimeout = {spec.get("timeout", 3)}\ndefault = "xnu"\n[kits]\nautoload = false\n{loader}'
              f'[[entry]]\nid = "xnu"\ntitle = "{spec.get("title", "UniXNU")}"\ntype = "xnu"\npath = "Payloads/kernel.macho"\n{initrd}'
              f'args = "{line}"\n')
    install = spec.get('install')
    if install:
        if not data:
            raise Error('board.toml [payload.install] needs a Data seed: pass --data-ramdisk FILE')
        titles, extra = install.get('confirm_titles', []), install.get('confirm_args', [])
        if not install.get('confirm') or not titles or len(titles) != len(extra):
            raise Error('board.toml [payload.install] needs confirm and equally long confirm_titles and confirm_args')
        # The second boot menu entry: the same kernel and seed behind a confirmation whose choices add a boot argument (for example the Data reset).
        config += (f'[[entry]]\nid = "install"\ntitle = {json.dumps(install.get("title", "Install and boot"))}\n'
                   f'confirm = {json.dumps(install["confirm"])}\nconfirm_titles = {json.dumps(titles)}\nconfirm_args = {json.dumps(extra)}\n'
                   f'type = "xnu"\npath = "Payloads/kernel.macho"\n{initrd}args = "{line}"\n')
    # A loaded configuration replaces the built-in menu (UniXNULib Config.c) and with it that menu's Restart and Power off.
    config += ('[[entry]]\nid = "reset"\ntitle = "Restart"\ntype = "action"\naction = "reset"\n'
               '[[entry]]\nid = "shutdown"\ntitle = "Power off"\ntype = "action"\naction = "shutdown"\n')
    (stage / 'EFI/UniXNU/unixnu.toml').write_text(config)
    for path in [stage, *stage.rglob('*')]:
        os.utime(path, (EPOCH, EPOCH))
    size = int(spec.get('size_mib', 192))
    content = sum(p.stat().st_size for p in stage.rglob('*') if p.is_file())
    if content > size * 1024 * 1024 * 0.95:
        raise Error(f'the payload files take {content >> 20} MiB; raise size_mib (now {size}) in board.toml [payload]')
    write_volume(stage, image, spec.get('volume', 'UNIXNU')[:11], size)
    data_report = {'kernel_sha256': sha256_file(kernel), 'payload_kernel_sha256': sha256_file(payloads / 'kernel.macho'),
                   'adt_sha256': sha256_file(payloads / 'kernel.macho.adt'), 'kernel_args': line,
                   'trust_cache_sha256': sha256_file(trust) if trust else None, 'gpu_addon_sha256': sha256_file(addon) if addon else None,
                   'data_ramdisk_sha256': sha256_file(data) if data else None, 'skip_setup': bool(getattr(args, 'skip_setup', False)), 'panic_screen': bool(spec.get('panic_screen')),
                   'payload_sha256': sha256_file(image), 'payload_bytes': image.stat().st_size, 'hardware_tested': False}
    report.write_text(json.dumps(data_report, indent=2) + '\n')
    shutil.rmtree(stage)
    log(f'payload: {image} ({image.stat().st_size >> 20} MiB)')
    return image
