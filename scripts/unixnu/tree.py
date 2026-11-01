"""Assemble the build tree from the resolved modules.

out/<device>/tree/ has the layout of this repository (drivers/ kits/ patches/ scripts/ package/)
plus refer/, build/ and .cache/ for the scripts that expect them. Modules are symbolic links to
their sources, so edits to a local module take effect on the next build; scripts are copied, since
they locate the tree from their own real path. The device package appears as kits/<kit>.
"""
import shutil
from pathlib import Path

from . import components
from .config import load_toml
from .util import Error, log


def _clear_links(directory):
    if directory.is_dir():
        for entry in directory.iterdir():
            if entry.is_symlink():
                entry.unlink()


def _link(target, link):
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(Path(target).resolve())


def _copy_scripts(source, destination):
    for path in sorted(Path(source).rglob('*')):
        relative = path.relative_to(source)
        if path.is_dir() or '__pycache__' in path.parts:
            continue
        target = destination / relative
        if target.is_symlink():
            target.unlink()
        # Content, not size and mtime: a pure move of code keeps the size, and a checkout can make
        # the source look older than a stale tree copy.
        if target.exists() and target.read_bytes() == path.read_bytes():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def assemble(ctx, modules):
    log(f'tree {ctx.tree}')
    tree = ctx.tree
    tree.mkdir(parents=True, exist_ok=True)
    for folder in ('drivers', 'kits', 'patches', 'refer'):
        _clear_links(tree / folder)
        (tree / folder).mkdir(exist_ok=True)
    for name in ('build', '.cache'):
        (tree / name).mkdir(exist_ok=True)
    if (ctx.root / 'components.toml').is_file():
        _link(ctx.root / 'components.toml', tree / 'components.toml')
    # Proprietary files (device repository: scripts/extract-files.py) stay in the device repository and are shared by every tree.
    firmware = ctx.device / '.cache/firmware'
    firmware.mkdir(parents=True, exist_ok=True)
    link = tree / '.cache/firmware'
    if link.is_symlink():
        link.unlink()
    if not link.exists():
        link.symlink_to(firmware)
    kit = ctx.board.get('board', {}).get('kit', ctx.name)
    for (kind, name), module in sorted(modules.items()):
        if kind in ('script', 'soc'):
            continue
        if module.path is None:
            if kind == 'refer':
                continue   # fetched when a step needs it
            raise Error(f'{kind} {name} has no source yet; run "unixnu fetch"')
        if kind == 'package':
            if name == 'main':
                _link(module.path, tree / 'package')
            else:
                _link(module.path, tree / 'kits' / kit)
        else:
            _link(module.path, tree / {'driver': 'drivers', 'kit': 'kits', 'patch': 'patches', 'refer': 'refer'}[kind] / name)
    for module, name in components.aliases(ctx, modules):
        if module.path is not None:
            _link(module.path, tree / {'driver': 'drivers', 'kit': 'kits'}[module.kind] / name)
    if not (tree / 'package').is_symlink():
        raise Error('no package module: this repository or --local-package must provide package/')
    (tree / 'scripts').mkdir(exist_ok=True)
    bases = [ctx.root]
    if ctx.soc:
        bases.append(ctx.soc.path)
    bases.append(ctx.device)
    for base in bases:
        if (base / 'scripts').is_dir():
            _copy_scripts(base / 'scripts', tree / 'scripts')
    compatibility = ctx.root / 'scripts/compatibility.toml'
    if compatibility.is_file():
        for alias, canonical in load_toml(compatibility).get('scripts', {}).items():
            target = tree / 'scripts' / canonical
            if not target.is_file():
                continue
            link = tree / 'scripts' / alias
            if not link.exists() or link.is_symlink():
                _link(target, link)
    components.sync_outputs(ctx, modules)
    return tree
