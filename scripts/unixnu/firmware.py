"""Device UEFI firmware: the EDK II build of a Mu-Silicium checkout (uefi-sheng), driven by board.toml [firmware]."""
import os
import shlex
import shutil
from pathlib import Path

from .config import load_toml
from .util import Error, clang_bin, git, log, run, tool


def uefi_config(ctx, uefi):
    fw = ctx.board.get('firmware')
    if not fw:
        raise Error('board.toml has no [firmware]')
    return fw, load_toml(uefi / 'Resources/Configs' / f'{fw["config"]}.toml')


def fd_path(ctx, uefi, target='DEBUG'):
    fw = ctx.board['firmware']
    return uefi / fw['fd'].format(target=target)


def build(ctx, modules, uefi, edk2, target='DEBUG'):
    log(f'firmware: {uefi.name}')
    fw, config = uefi_config(ctx, uefi)
    for name in ('clang', 'python3', 'make'):
        tool(name)
    base, size = config['uefi_fd']['base'], config['uefi_fd']['size']
    if fw.get('submodules'):
        # Upstream Mu-Silicium submodules the board needs (Mu_Basecore is provided separately).
        log('firmware: initializing submodules of the Mu-Silicium checkout')
        run(['git', '-C', uefi, 'submodule', 'update', '--init', '--depth', '1', '--', *fw['submodules']])
    for entry in [] if ctx.args.skip_preflight else fw.get('preflight', []):
        parts = shlex.split(entry)
        script = Path(parts[0]) if Path(parts[0]).is_absolute() else ctx.tree / parts[0]
        run(['python3', script, *parts[1:]], cwd=ctx.tree,
            env=dict(os.environ, UNIXNU_UEFI=str(uefi), UNIXNU_DEVICE=str(ctx.device)), log_file=ctx.logs / 'firmware-preflight.log')
    defines = {'FD_BASE': hex(base), 'FD_SIZE': hex(size), 'FD_BLOCKS': str(size // 0x1000)}
    defines.update({key: str(value) for key, value in fw.get('defines', {}).items()})
    fields = {'uefi': str(uefi), 'edk2': str(edk2), 'tree': str(ctx.tree)}
    packages = ':'.join(item.format(**fields) for item in fw['packages'])
    tools = edk2 / 'BaseTools'
    if not (tools / 'Source/C/bin/GenFw').is_file():
        log('firmware: building BaseTools')
        run(['make', '-C', tools / 'Source/C', f'-j{ctx.jobs}'], log_file=ctx.logs / 'basetools.log')
    conf = ctx.work / 'edk2-conf'
    conf.mkdir(parents=True, exist_ok=True)
    for name in ('target', 'tools_def', 'build_rule'):
        if not (conf / f'{name}.txt').is_file():
            shutil.copy(tools / 'Conf' / f'{name}.template', conf / f'{name}.txt')
    env = dict(os.environ, WORKSPACE=str(uefi), EDK_TOOLS_PATH=str(tools), CONF_PATH=str(conf), PACKAGES_PATH=packages,
               PYTHON_COMMAND='python3',
               PATH=os.pathsep.join([str(tools / 'BinWrappers/PosixLike'), str(tools / 'Source/C/bin'), os.environ['PATH']]))
    env.setdefault('CLANG_BIN', clang_bin(ctx.work / 'toolchain'))
    # EDK II embeds the build time; pin it to the commit time so the same sources give the same firmware.
    env.setdefault('SOURCE_DATE_EPOCH', git(uefi, 'log', '-1', '--format=%ct').strip())
    applied = []
    try:
        # Board patches for the shared edk2 checkout: applied for the build, always reverted.
        for patch in fw.get('patches', []):
            path = uefi / patch
            run(['git', '-C', edk2, 'apply', '--check', path])
            run(['git', '-C', edk2, 'apply', path])
            applied.append(path)
        command = ['build', '-p', fw['dsc'], '-a', 'AARCH64', '-b', target, '-t', 'CLANGPDB', '-n', str(ctx.jobs)]
        for key, value in defines.items():
            command += ['-D', f'{key}={value}']
        run(command, cwd=uefi, env=env, log_file=ctx.logs / 'firmware.log')
    finally:
        for path in reversed(applied):
            git(edk2, 'apply', '--reverse', str(path))
    fd = fd_path(ctx, uefi, target)
    if not fd.is_file() or fd.stat().st_size != size:
        raise Error(f'{fd} missing or not {size:#x} bytes')
    log(f'firmware: {fd}')
    return fd
