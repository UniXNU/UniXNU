"""UniXNU: the EDK II build of package/, output under out/<device>/package."""
import os
import shutil

from .util import Error, clang_bin, expand, log, run, tool


def output_dir(tree, target='DEBUG'):
    """Locate package outputs for an assembled tree or a standalone checkout."""
    candidates = [tree.parent / 'package/Build/Out' / f'AARCH64-{target}',
                  tree / 'package/Build/Out' / f'AARCH64-{target}']
    return next((path for path in candidates if path.is_dir()), candidates[0])


def edk2_dir(ctx, modules):
    given = ctx.option('edk2', 'UNIXNU_EDK2')
    if given:
        path = given
    elif ('refer', 'edk2') in modules and modules[('refer', 'edk2')].path:
        path = modules[('refer', 'edk2')].path
    else:
        raise Error('no edk2 tree: pass --edk2 DIR (a Mu_Basecore checkout) or run "unixnu fetch" for the edk2 source')
    if not (path / 'MdePkg/MdePkg.dec').is_file():
        raise Error(f'{path} is not an edk2 or Mu_Basecore tree')
    return path


def build(ctx, modules, target='DEBUG', toolchain='CLANGPDB'):
    log('package: UniXNU')
    edk2 = edk2_dir(ctx, modules)
    tool('clang', 'brew install llvm')
    env = dict(os.environ, UNIXNU_EDK2=str(edk2), UNIXNU_BUILD_DIR=str(ctx.work / 'package'), JOBS=str(ctx.jobs))
    selected_tools = ctx.option('clang_bin', 'CLANG_BIN')
    if selected_tools:
        env['CLANG_BIN'] = str(selected_tools) + '/'
    elif toolchain == 'CLANGPDB' and 'CLANG_BIN' not in env:
        env['CLANG_BIN'] = clang_bin(ctx.work / 'toolchain')
    (ctx.work / 'package').mkdir(parents=True, exist_ok=True)
    run(['bash', ctx.tree / 'package/build.sh', '-b', target, '-t', toolchain], cwd=ctx.tree / 'package', env=env,
        log_file=ctx.logs / 'package.log')
    log(f'package: outputs in {ctx.work / "package/Build/Out"}')
