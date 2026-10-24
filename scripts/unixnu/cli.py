"""Command line of the UniXNU build driver."""
import argparse
import json
import platform
import shutil
import sys

from . import bootimg, components, feeds, firmware, ipsw, kernel, package, patches, payload, profiles, tree, userdata
from .config import LOCAL_KINDS, Context, parse_config
from .util import Error, expand, git, log

STEPS = ('kernel', 'package', 'firmware', 'payload')
OPTIONAL_STEPS = ('userdata',)   # large; built only when named


def common():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument('--config', metavar='FILE', help='local build inputs (default: unixnu.local.toml in the UniXNU checkout)')
    p.add_argument('-D', '--device', metavar='DIR', help='device repository (remembered; or UNIXNU_DEVICE)')
    p.add_argument('--out', metavar='DIR', help='output root (default: out/ here, or UNIXNU_OUT)')
    p.add_argument('-j', '--jobs', type=int, help='parallel jobs')
    p.add_argument('--local', metavar='DIR', help='directory laid out like this repository; its drivers, kits, patches, scripts and package are used')
    for kind in LOCAL_KINDS:
        p.add_argument(f'--local-{kind}', metavar='DIR', help=f'use DIR as the {kind} directory (beats --local)')
    p.add_argument('--local-module', action='append', metavar='[KIND:]NAME=PATH', help='use PATH for one module (beats everything)')
    p.add_argument('--uefi', metavar='DIR', help='Mu-Silicium checkout for the device (uefi-sheng); or UNIXNU_UEFI')
    p.add_argument('--edk2', metavar='DIR', help='Mu_Basecore checkout; or UNIXNU_EDK2')
    p.add_argument('--kernelcache', metavar='FILE', help='original decompressed kernelcache; or UNIXNU_KERNELCACHE')
    p.add_argument('--skip-preflight', action='store_true', help='skip the board preflight scripts of the firmware step')
    p.add_argument('--kernel', metavar='FILE', help='prelinked kernel Mach-O for the payload (default: the kernel step output)')
    p.add_argument('--kernel-arg', action='append', metavar='NAME[=VALUE]', help='extra kernel boot argument (repeatable)')
    p.add_argument('--trust-cache', metavar='FILE', help='trust cache bundle for the payload')
    p.add_argument('--owner-trust-cache', metavar='FILE', help='owner-signed trust cache bundle that carries the original caches and extra modules; replaces --trust-cache and skips the board allow-list')
    p.add_argument('--skip-setup', action='store_true', help='mark Setup as done in the Data seed, so the Hello pages are skipped (needs --data-ramdisk; optional)')
    p.add_argument('--data-ramdisk', metavar='FILE', help='Data ramdisk seed for the payload (an input; not built here)')
    p.add_argument('--gpu-addon', metavar='FILE', help='GPU addon file (scripts/make-gpu-addon.py) the kernel writes into the Data volume at boot')
    p.add_argument('--unique-chip-id', metavar='HEX', help='platform seed for the device tree; or UNIXNU_UNIQUE_CHIP_ID')
    p.add_argument('--ipsw', metavar='PATH_OR_URL', help='the target IPSW: a local file or an https URL (default: url of board.toml [ipsw]); or UNIXNU_IPSW')
    p.add_argument('--dry-run', action='store_true', help='userdata: check sizes and pins, write nothing')
    p.add_argument('--target', choices=('DEBUG', 'RELEASE'), help='EDK II build target')
    return p


def parser():
    top = argparse.ArgumentParser(prog='unixnu', description='Build UniXNU, the XNU kernel and the boot image for a device repository.')
    sub = top.add_subparsers(dest='command', required=True)
    c = common()
    d = sub.add_parser('defconfig', parents=[c], help='select configs/NAME in the device repository')
    d.add_argument('name', nargs='?', help='defconfig name; omit to list')
    f = sub.add_parser('fetch', parents=[c], help='update module submodules, shallow-fetch git sources and write unixnu.lock')
    f.add_argument('names', nargs='*', help='sources to fetch (default: all)')
    f.add_argument('--update', action='store_true', help='ignore the lock and move to the newest ref')
    sub.add_parser('tree', parents=[c], help='assemble the build tree')
    b = sub.add_parser('build', parents=[c], help='build kernel, package and firmware')
    b.add_argument('steps', nargs='*', choices=STEPS + OPTIONAL_STEPS + ('all', 'prelink'), default=['all'])
    for step in STEPS + OPTIONAL_STEPS + ('prelink',):
        shortcut = sub.add_parser(step, parents=[c], help=f'alias for build {step}')
        shortcut.set_defaults(steps=[step])
    i = sub.add_parser('bootimg', parents=[c], help='pack the boot image from the firmware volume and a device tree')
    i.add_argument('--fd', metavar='FILE', help='firmware volume with UniXNU, DarwinBoot and payload filesystem support (default: build firmware output under --uefi)')
    i.add_argument('--dtb', metavar='FILE', help='compiled device tree; or UNIXNU_DTB')
    i.add_argument('--ramdisk', metavar='FILE', help='ramdisk image, or none (default: the payload step output when present, else empty)')
    i.add_argument('-o', '--output', metavar='FILE', help='output (default: out/<device>/boot/boot.img)')
    w = sub.add_parser('ipsw', parents=[c], help='show or extract the components of the target IPSW')
    w.add_argument('action', choices=('info', 'fetch'))
    w.add_argument('components', nargs='*', help='components to extract (default: the small ones the board lists)')
    status = sub.add_parser('status', parents=[c], help='show the device, configuration and where each module comes from')
    status.add_argument('--json', action='store_true', help='print resolved configuration as JSON without fetching sources')
    sub.add_parser('clean', parents=[c], help='remove the build output of the device (keeps fetched sources)')
    return top


def need_uefi(ctx):
    uefi = ctx.option('uefi', 'UNIXNU_UEFI')
    if not uefi:
        raise Error('the firmware needs a Mu-Silicium checkout: --uefi DIR (or UNIXNU_UEFI)')
    if not (uefi / 'Resources/Scripts/mkbootimg.py').is_file():
        raise Error(f'{uefi} is not a Mu-Silicium checkout')
    return uefi


REFERENCES = {'kernel': ('xnu', 'libplatform', 'libdispatch', 'AvailabilityVersions', 'libpthread', 'corecrypto-2023', 'IOStorageFamily'), 'package': ('edk2',), 'firmware': ('edk2',)}


def prepare(ctx, steps=()):
    """Update module submodules, resolve modules, fetch the git references and assemble the tree."""
    feeds.update_submodules(ctx)
    modules = feeds.resolve(ctx)
    wanted = {name for step in steps for name in REFERENCES.get(step, ())}
    feeds.fetch(ctx, modules, only={m.name for m in modules.values() if m.origin == 'git' and (m.kind != 'refer' or m.name in wanted)})
    tree.assemble(ctx, modules)
    return modules


def cmd_defconfig(ctx):
    configs = ctx.device / 'configs'
    names = sorted(p.name for p in configs.glob('*_defconfig')) if configs.is_dir() else []
    if not ctx.args.name:
        print('\n'.join(names) or 'no defconfigs')
        return
    source = configs / ctx.args.name
    if not source.is_file():
        raise Error(f'{source} not found; available: {", ".join(names) or "none"}')
    inputs = []
    if ctx.schema_version == 2:
        inputs = [profiles.resolve_path(ctx, entry) for entry in ctx.board.get('kernel', {}).get('config_fragments', [])]
    inputs.append(source)
    chunks = []
    for path in inputs:
        if not path.is_file():
            raise Error(f'configuration fragment missing: {path}')
        contents = path.read_text()
        parse_config(contents)
        chunks.append(contents.rstrip() + '\n')
    ctx.work.mkdir(parents=True, exist_ok=True)
    ctx.config_path.write_text('\n'.join(chunks))
    ctx.remember_config(ctx.args.name)
    log(f'configuration {ctx.args.name} -> {ctx.config_path}')


def cmd_fetch(ctx):
    wanted = set(ctx.args.names) or None
    soc_commits = {}
    if ctx.soc and (wanted is None or ctx.soc.name in wanted):
        previous = ctx.soc.commit
        soc_commits = feeds.fetch(ctx, {('soc', ctx.soc.name): ctx.soc}, update=ctx.args.update)
        if soc_commits and ctx.soc.commit != previous:
            feeds.lock_write(ctx, {**feeds.lock_read(ctx), **soc_commits})
            ctx.board = profiles.load(ctx, allow_fetch=True)
    feeds.update_submodules(ctx)
    modules = feeds.resolve(ctx)
    commits = {**soc_commits, **feeds.fetch(ctx, modules, update=ctx.args.update, only=wanted)}
    if commits:
        feeds.lock_write(ctx, {**feeds.lock_read(ctx), **commits})
        log(f'wrote {ctx.lock_path}')


def cmd_build(ctx):
    ctx.refuse_example()
    steps = ctx.args.steps
    if 'all' in steps:
        steps = list(STEPS)
    if 'userdata' in steps:
        userdata.build(ctx, ctx.args.dry_run)
        steps = [step for step in steps if step != 'userdata']
        if not steps:
            return
    if 'kernel' in steps:
        ctx.need_config()
    if 'firmware' in steps:
        need_uefi(ctx)   # fail before fetching anything
    modules = prepare(ctx, steps + (['kernel'] if 'prelink' in steps else []))
    if 'kernel' in steps:
        kernel.build(ctx, modules)
        kernel.prelink(ctx)
    elif 'prelink' in steps:
        kernel.prelink(ctx)
    if 'package' in steps:
        package.build(ctx, modules, ctx.args.target)
    if 'payload' in steps:
        ctx.uefi = ctx.option('uefi', 'UNIXNU_UEFI')
        payload.build(ctx)
    if 'firmware' in steps:
        firmware.build(ctx, modules, need_uefi(ctx), package.edk2_dir(ctx, modules), ctx.args.target)


def cmd_bootimg(ctx):
    ctx.refuse_example()
    uefi = need_uefi(ctx)
    fd = expand(ctx.args.fd) if ctx.args.fd else firmware.fd_path(ctx, uefi, ctx.args.target)
    dtb = ctx.option('dtb', 'UNIXNU_DTB')
    ramdisk = None
    if ctx.args.ramdisk and ctx.args.ramdisk != 'none':
        ramdisk = expand(ctx.args.ramdisk)
    elif not ctx.args.ramdisk and payload.paths(ctx)[1].is_file():
        ramdisk = payload.paths(ctx)[1]
        log(f'ramdisk: {ramdisk} (use --ramdisk none for an empty one)')
    if ramdisk is None:
        log('ramdisk: empty; build payload or pass --ramdisk FILE to include configured boot entries')
    bootimg.build(ctx, uefi, fd, dtb, ramdisk, expand(ctx.args.output) if ctx.args.output else None)


def cmd_ipsw(ctx):
    source = ipsw.Ipsw(ctx)
    components = ctx.args.components or ctx.board['ipsw'].get('fetch', [])
    if ctx.args.action == 'info':
        print(f'{source.manifest["ProductVersion"]} ({source.manifest["ProductBuildVersion"]}) '
              f'{source.config["device_class"]}  {"remote" if source.remote else "local"}')
        for name in sorted(source.identity['Manifest']):
            if source.identity['Manifest'][name].get('Info', {}).get('Path'):
                path, size, _ = source.info(name)
                print(f'{size:>12}  {name:30} {path}')
        return
    for component in components:
        if component == 'KernelCache':
            print(ipsw.kernelcache(ctx, source))
        else:
            print(source.extract(component))


def cmd_status(ctx):
    modules = feeds.resolve(ctx)
    if ctx.soc:
        modules[('soc', ctx.soc.name)] = ctx.soc
    locked = feeds.lock_read(ctx)
    resolved = []
    for (kind, name), module in sorted(modules.items()):
        revision = module.commit
        if module.path and not revision:
            try:
                revision = git(module.path, 'rev-parse', 'HEAD').strip()
            except Error:
                pass
        spec = getattr(module, 'spec', {})
        identity = components.source_identity(ctx, module)
        resolved.append({'kind': kind, 'name': name, 'path': str(module.path) if module.path else None,
                         'origin': module.origin, 'local': module.local, 'revision': revision,
                         'pin': None if module.local else feeds.pinned_revision(ctx, module, locked) or spec.get('revision'),
                         'scope': spec.get('scope'), 'repository': (module.source or {}).get('git') or
                         ('https://' + identity if identity else spec.get('repository'))})
    patch_order = patches.plan(ctx, modules) if ctx.schema_version == 2 else []
    if ctx.args.json:
        print(json.dumps({'schema_version': ctx.schema_version, 'device': str(ctx.device), 'name': ctx.name,
                          'output': str(ctx.work), 'configuration': ctx.config_name,
                          'build_config': ctx.args.build_config,
                          'config_path': str(ctx.config_path), 'configured': ctx.config_path.is_file(),
                          'profiles': {key: str(value) for key, value in ctx.profile_roots.items()},
                          'configuration_sources': [str(path) for path in ctx.profile_files],
                          'board': ctx.board, 'components': ctx.component_specs, 'modules': resolved,
                          'patch_order': [str(path) for path in patch_order]}, indent=2))
        return
    print(f'device   {ctx.device} ({ctx.name})' + ('  [EXAMPLE]' if ctx.example else ''))
    print(f'output   {ctx.work}')
    if ctx.args.build_config:
        print(f'inputs   {ctx.args.build_config}')
    print(f'config   {ctx.config_path if ctx.config_path.is_file() else "none (run defconfig)"}')
    if ctx.schema_version == 2:
        for name, path in ctx.profile_roots.items():
            print(f'profile  {name:24} {path}')
        for module in resolved:
            if module['scope']:
                print(f'component {module["name"]:23} {module["scope"]}')
        for index, path in enumerate(patch_order, 1):
            print(f'patch    {index:02} {path}')
    unpinned = []
    for (kind, name), module in sorted(modules.items()):
        extra = ''
        if module.origin == 'git':
            pinned = feeds.pinned_revision(ctx, module, locked)
            extra = f' pinned {pinned[:12]}' if pinned else ' NOT LOCKED'
        elif module.local:
            try:
                extra = ' (dirty)' if git(module.path, 'status', '--porcelain', '--', '.').strip() else ' (clean)'
            except Error:
                extra = ' (not a git work tree)'
            unpinned.append(f'{kind}:{name}')
        print(f'{kind:8} {name:24} {module.origin}{extra}')
    if unpinned:
        print(f'\nnot reproducible: {len(unpinned)} local source(s) are not pinned by unixnu.lock')


def cmd_clean(ctx):
    for name in ('tree', 'logs', 'kernel', 'package', 'boot', 'edk2-conf'):
        shutil.rmtree(ctx.work / name, ignore_errors=True)
    log(f'cleaned {ctx.work}')


def main(argv=None):
    if sys.version_info < (3, 11):
        sys.exit('unixnu needs Python 3.11 or newer')
    if platform.system() == 'Linux':
        print('unixnu: on Linux the kernel step uses the toolchain of scripts/linux/setup-toolchain.py; '
              '--skip-setup and seed-data-grow need macOS hdiutil', file=sys.stderr)
    elif platform.system() != 'Darwin':
        print('unixnu: developed and tested on macOS and Linux only; the kernel step needs Xcode or the Linux toolchain, '
              'and --skip-setup needs hdiutil', file=sys.stderr)
    args = parser().parse_args(argv)
    if args.command in STEPS + OPTIONAL_STEPS + ('prelink',):
        args.command = 'build'
    try:
        ctx = Context(args)
        {'defconfig': cmd_defconfig, 'fetch': cmd_fetch, 'tree': lambda c: prepare(c), 'build': cmd_build,
         'bootimg': cmd_bootimg, 'ipsw': cmd_ipsw, 'status': cmd_status, 'clean': cmd_clean}[args.command](ctx)
    except Error as error:
        sys.exit(f'unixnu: {error}')
    except KeyboardInterrupt:
        sys.exit(130)
