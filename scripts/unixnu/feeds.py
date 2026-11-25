"""Module sources: local directories, in-tree modules and shallow, sparse git checkouts.

A module is a driver, kit, patch set or the package, identified by (kind, name). Candidates are
taken in this order, first one that exists wins:

  1. --local-module NAME=PATH
  2. --local-<kind> DIR              (DIR/NAME)
  3. --local DIR                     (DIR/<kind>/NAME, same layout as this repository)
  4. a "local" entry in feeds.toml or the ignored local.toml of the device repository
  5. the device repository's own directories
  6. this repository's own directories, including module submodules
  7. a git source from feeds.toml: shallow, blobless, sparse checkout of the module path

Module submodules are checked out by `git submodule update --init --recursive`. Feed sources are
separate checkouts. Nothing fetched or linked is copied into either repository.
"""
import hashlib
import os
from pathlib import Path

from .config import KINDS, LOCAL_KINDS, load_toml
from .util import Error, expand, git, log, run


class Module:
    def __init__(self, kind, name, path=None, origin='', source=None):
        self.kind, self.name, self.path, self.origin, self.source = kind, name, path, origin, source
        self.commit = None

    @property
    def local(self):
        return self.origin.startswith('local')

    def __repr__(self):
        return f'{self.kind}:{self.name} <{self.origin}> {self.path}'


def read_sources(ctx):
    """Entries of every feeds.toml (this repository, then the device repository) and the device local.toml."""
    sources, local = {}, {}

    def source_path(base, value):
        path = Path(os.path.expandvars(value)).expanduser()
        if ctx.schema_version == 2 and not path.is_absolute():
            path = base / path
        return str(expand(path))

    def add_sources(path, content):
        for item in content.get('source', []):
            entry = dict(item)
            kind, name = entry.get('kind'), entry.get('name')
            if kind not in KINDS or not name:
                raise Error(f'{path}: every [[source]] needs name and kind in {sorted(KINDS)}')
            if entry.get('local'):
                entry['local'] = source_path(path.parent, entry['local'])
            sources[(kind, name)] = entry

    roots = getattr(ctx, 'profile_roots', {})
    bases = [ctx.root] + [roots[key] for key in ('arch', 'soc', 'os') if key in roots] + [ctx.device]
    for base in bases:
        path = base / 'feeds.toml'
        files = [path]
        if base != ctx.root and base != ctx.device:
            files.insert(0, base / ('soc.toml' if base == roots.get('soc') else 'profile.toml'))
        for path in files:
            if not path.is_file():
                continue
            add_sources(path, load_toml(path))
    os_profile = ctx.board.get('os', {}) if ctx.schema_version == 2 else {}
    if os_profile and ('refer', 'xnu') in sources:
        xnu = dict(sources[('refer', 'xnu')])
        for key, field in (('xnu_revision', 'commit'), ('xnu_version', 'version'), ('darwin', 'darwin'),
                           ('driverkit_tag', 'driverkit_tag'), ('trustcache_tag', 'trustcache_tag')):
            if os_profile.get(key):
                xnu[field] = os_profile[key]
        if os_profile.get('xnu_version'):
            xnu['ref'] = 'xnu-' + os_profile['xnu_version']
        sources[('refer', 'xnu')] = xnu
    path = ctx.device / 'local.toml'
    if path.is_file():
        local = load_toml(path)
        if ctx.schema_version == 2:
            add_sources(path, local)
            local['local'] = {kind: source_path(ctx.device, value)
                              for kind, value in local.get('local', {}).items()}
    return sources, local


def lock_read(ctx):
    if not ctx.lock_path.is_file():
        return {}
    return {name: values['commit'] for name, values in load_toml(ctx.lock_path).get('source', {}).items()}


def lock_write(ctx, commits):
    lines = ['# Resolved git sources, written by "unixnu fetch". Local sources are never recorded.']
    for name in sorted(commits):
        lines += ['', f'[source."{name}"]', f'commit = "{commits[name]}"']
    ctx.lock_path.write_text('\n'.join(lines) + '\n')


def _children(directory):
    directory = Path(directory)
    return sorted(p.name for p in directory.iterdir() if p.is_dir() and not p.name.startswith('.')) if directory.is_dir() else []


def _cli_locals(args):
    """(per-module overrides, per-kind directories, local root) from the command line."""
    modules = {}
    for item in args.local_module or []:
        if '=' not in item:
            raise Error(f'--local-module needs NAME=PATH (or KIND:NAME=PATH): {item}')
        key, path = item.split('=', 1)
        kind, _, name = key.partition(':') if ':' in key else ('', '', key)
        modules[(kind, name)] = expand(path)
    kinds = {}
    for kind in LOCAL_KINDS:
        value = getattr(args, 'local_' + kind, None)
        if value:
            kinds[kind] = expand(value)
    return modules, kinds, expand(args.local) if args.local else None


def _need(path, what):
    if not Path(path).is_dir():
        raise Error(f'{what}: {path} is not a directory')
    return Path(path)


def resolve(ctx):
    """Map (kind, name) to a Module. Git modules are resolved to a clone path later by fetch()."""
    sources, local_file = read_sources(ctx)
    cli_modules, cli_kinds, cli_root = _cli_locals(ctx.args)
    if cli_root is not None:
        _need(cli_root, '--local')
    for (kind, name) in cli_modules:
        if kind and kind not in KINDS:
            raise Error(f'--local-module: unknown kind {kind}')
    result = {}

    def add(kind, name, path, origin, source=None):
        result.setdefault((kind, name), Module(kind, name, path, origin, source))

    plural = {kind: KINDS[kind] for kind in KINDS}
    # 1: --local-module
    for (kind, name), path in cli_modules.items():
        _need(path, f'--local-module {name}')
        targets = [kind] if kind else [k for k in KINDS if (k, name) in sources or any(
            (base / plural[k] / name).is_dir() for base in (ctx.device, ctx.root))]
        if not targets and (ctx.root / 'components.toml').is_file():
            from .components import catalog
            targets = list({spec['kind'] for spec in catalog(ctx).values()
                            if name in (spec['id'], spec.get('legacy_name'))})
        if not targets:
            raise Error(f'--local-module {name}: unknown module; use KIND:NAME=PATH to add a new one')
        if len(targets) > 1:
            raise Error(f'--local-module {name} is ambiguous ({", ".join(targets)}); use KIND:NAME=PATH')
        add(targets[0], name, path, 'local (--local-module)')
    # 2 and 3: per-kind directories and the local root
    for kind in KINDS:
        directory = cli_kinds.get(plural[kind])
        origin = f'local (--local-{plural[kind]})'
        if directory is None and cli_root is not None and (cli_root / plural[kind]).is_dir():
            directory, origin = cli_root / plural[kind], 'local (--local)'
        if directory is None or kind in ('refer', 'script', 'soc'):
            continue
        if kind == 'package':
            add('package', 'main', _need(directory, '--local-package'), origin)
            continue
        for name in _children(_need(directory, f'--local-{plural[kind]}')):
            add(kind, name, directory / name, origin)
    # 4: local entries of the configuration files
    for (kind, name), entry in sources.items():
        if entry.get('local'):
            add(kind, name, _need(expand(entry['local']), f'source {name}'), 'local (feeds)')
    for kind, directory in local_file.get('local', {}).items():
        if kind in LOCAL_KINDS and kind not in cli_kinds and kind != 'package':
            for name in _children(_need(expand(directory), f'local.toml {kind}')):
                add({v: k for k, v in KINDS.items()}[kind], name, expand(directory) / name, 'local (local.toml)')
    # 5 and 6: the device repository, then this repository
    bases = [(ctx.device, 'device')]
    if getattr(ctx, 'soc', None):
        bases.append((ctx.soc.path, 'soc'))
    bases.append((ctx.root, 'base'))
    for base, label in bases:
        for kind, folder in KINDS.items():
            if kind in ('refer', 'script', 'soc'):
                continue
            if kind == 'package':
                if (base / 'package').is_dir():
                    add('package', 'main' if base == ctx.root else 'device', base / 'package', label)
                continue
            for name in _children(base / folder):
                add(kind, name, base / folder / name, label)
    # 7: git sources
    for (kind, name), entry in sources.items():
        if entry.get('git') and kind != 'soc':
            add(kind, name, None, 'git', entry)
    result = {key: module for key, module in result.items() if key[0] != 'soc'}
    if ctx.schema_version == 2:
        from . import components
        result = components.resolve(ctx, result)
    attach_cached(ctx, result)
    ctx.modules = result
    return result


def update_submodules(ctx):
    """Check out module submodules recorded by this repository and the device repository."""
    bases = [ctx.root, ctx.device]
    if getattr(ctx, 'soc', None):
        bases.append(ctx.soc.path)
    for base in bases:
        if not (base / '.gitmodules').is_file():
            continue
        # Linked git worktrees share .git/modules/*/config with the primary checkout;
        # running `git submodule update` inside a linked worktree overwrites core.worktree
        # in the primary checkout. Skip when all submodules are already populated worktrees.
        if (base / '.git').is_file():
            log(f'submodules {base}: linked worktree, preserving primary .git/modules configs')
            continue
        log(f'submodules {base}')
        # A submodule with modified tracked files is under local development; leave its checkout alone.
        dirty = git(base, 'submodule', 'foreach', '--quiet',
                    'git diff --quiet HEAD -- 2>/dev/null || echo "$sm_path"', capture=True).split()
        for path in dirty:
            log(f'submodules: {path} has local changes, not updated')
        if not dirty:
            git(base, 'submodule', 'update', '--init', '--recursive')
            continue
        paths = [line.split()[1] for line in git(base, 'submodule', 'status', capture=True).splitlines()
                 if line.split()[1] not in dirty]
        if paths:
            git(base, 'submodule', 'update', '--init', '--recursive', '--', *paths)


def _clone_dir(ctx, entry, revision=None):
    # Commit-specific directories allow targets to resolve different source pins.
    revision = (revision or entry.get('commit') or entry.get('ref', '')) if ctx.schema_version == 2 else entry.get('ref', '')
    key = hashlib.sha1(f'{entry["git"]}\n{revision}'.encode()).hexdigest()[:8]
    return ctx.feeds_dir / f'{Path(entry["git"]).stem}-{key}'


def pinned_revision(ctx, module, locked):
    entry = module.source or {}
    recorded = locked.get(module.name) or locked.get(entry.get('name'))
    if ctx.schema_version == 2:
        return entry.get('commit') or recorded
    return recorded or entry.get('commit')


def attach_cached(ctx, modules):
    locked = lock_read(ctx)
    for module in modules.values():
        if module.origin != 'git':
            continue
        wanted = pinned_revision(ctx, module, locked)
        directory = _clone_dir(ctx, module.source, wanted)
        if not (directory / '.git').exists():
            continue
        try:
            current = git(directory, 'rev-parse', 'HEAD').strip()
        except Error:
            continue
        if wanted and current != wanted:
            continue
        path = directory / module.source.get('path', '')
        if path.exists():
            module.path, module.commit = path, current


def resolve_soc(ctx, name, allow_fetch):
    sources, local = read_sources(ctx)
    cli_modules, _, cli_root = _cli_locals(ctx.args)
    entry = sources.get(('soc', name))
    override = cli_modules.get(('soc', name)) or cli_modules.get(('', name))
    if override:
        return Module('soc', name, _need(override, f'soc {name}'), 'local (--local-module)')
    if cli_root and (cli_root / 'socs' / name).is_dir():
        return Module('soc', name, cli_root / 'socs' / name, 'local (--local)')
    if entry and entry.get('local'):
        return Module('soc', name, _need(entry['local'], f'soc {name}'), 'local (feeds)')
    if not entry or not entry.get('git'):
        raise Error(f'feeds.toml needs a source with kind = "soc" and name = "{name}"')
    if not (entry.get('commit') or lock_read(ctx).get(name)):
        raise Error(f'soc source {name} needs a pinned commit')
    module = Module('soc', name, None, 'git', entry)
    modules = {('soc', name): module}
    attach_cached(ctx, modules)
    if module.path is None and allow_fetch:
        fetch(ctx, modules)
    if module.path is None:
        raise Error(f'SoC {name} is not cached; run unixnu fetch -D {ctx.device}')
    return module


def fetch(ctx, modules, update=False, only=None):
    """Shallow, blobless, sparse checkout of git modules (all, or the named ones); returns {source name: commit}.

    A clone already at the wanted commit is not contacted again."""
    locked = {} if update else lock_read(ctx)
    groups = {}
    for module in modules.values():
        if module.origin == 'git' and (only is None or module.name in only):
            groups.setdefault(_clone_dir(ctx, module.source, pinned_revision(ctx, module, locked)), []).append(module)
    commits = {}
    for directory, members in groups.items():
        entry = members[0].source
        paths = sorted({m.source['path'] for m in members if m.source.get('path')})
        sparse = bool(paths) and all(m.source.get('path') for m in members)
        target = next((pinned_revision(ctx, m, locked) for m in members if pinned_revision(ctx, m, locked)), None) or entry.get('ref') or 'HEAD'
        current = None
        if (directory / '.git').is_dir():
            try:
                current = git(directory, 'rev-parse', 'HEAD').strip()
            except Error:
                current = None
        if current and current == target and (not sparse or all((directory / path).exists() for path in paths)):
            _attach(members, directory, current, commits)
            continue
        log(f'fetch {entry["git"]} {target[:12]}' + (f' ({", ".join(paths)})' if sparse else ''))
        if not (directory / '.git').is_dir():
            directory.mkdir(parents=True, exist_ok=True)
            git(directory, 'init', '-q')
            git(directory, 'remote', 'add', 'origin', entry['git'])
        if sparse:
            git(directory, 'sparse-checkout', 'set', '--cone', *paths)
            git(directory, 'config', 'remote.origin.promisor', 'true')
            git(directory, 'config', 'remote.origin.partialclonefilter', 'blob:none')
            run(['git', '-C', directory, 'fetch', '-q', '--depth', '1', '--filter=blob:none', 'origin', target])
        else:
            git(directory, 'sparse-checkout', 'disable')
            run(['git', '-C', directory, 'fetch', '-q', '--depth', '1', 'origin', target])
        git(directory, 'checkout', '-q', '--detach', 'FETCH_HEAD')
        if entry.get('submodules'):
            # Upstream trees such as edk2 need their own submodules. UniXNU module submodules are
            # updated from the root and device repositories by update_submodules().
            run(['git', '-C', directory, 'submodule', 'update', '--init', '--depth', '1', '--', *entry['submodules']])
        _attach(members, directory, git(directory, 'rev-parse', 'HEAD').strip(), commits)
    return commits


def _attach(members, directory, commit, commits):
    for module in members:
        subpath = module.source.get('path', '')
        module.path = directory / subpath if subpath else directory
        if not module.path.exists():
            raise Error(f'{module.source["git"]} at {commit[:12]} has no {subpath}')
        module.commit = commit
        commits[module.name] = commit
