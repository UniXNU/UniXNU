"""Component identities, dependency order, and archive recipes."""
import re
from pathlib import Path

from .config import load_toml
from .util import Error, git


def catalog(ctx):
    entries = load_toml(ctx.root / 'components.toml').get('component', [])
    result = {}
    for entry in entries:
        identifier = entry.get('id')
        if not identifier or identifier in result:
            raise Error(f'components.toml: missing or duplicate component id {identifier!r}')
        result[identifier] = entry
    return result


def selected(ctx, modules=None):
    entries = catalog(ctx)
    order, active, done = [], [], set()

    def visit(identifier):
        if identifier not in entries:
            for spec in entries.values():
                if spec.get('legacy_name') != identifier:
                    continue
                candidates = [modules.get((spec['kind'], name)) for name in (identifier, spec['id'])] if modules else []
                if any(candidate and official_alias(ctx, candidate, spec) for candidate in candidates):
                    identifier = spec['id']
                    break
        if identifier in done:
            return
        if identifier in active:
            raise Error('component dependency cycle: ' + ' -> '.join(active + [identifier]))
        entry = entries.get(identifier)
        if entry is None:
            raise Error(f'unknown component: {identifier}')
        active.append(identifier)
        for dependency in entry.get('dependencies', []):
            visit(dependency)
        active.pop()
        done.add(identifier)
        order.append(entry)

    for identifier in ctx.board.get('components', {}).get('include', []):
        visit(identifier)
    return order


def repository_identity(url):
    value = re.sub(r'^git@([^:]+):', r'https://\1/', url or '')
    value = re.sub(r'^ssh://git@', 'https://', value)
    value = re.sub(r'^https?://', '', value).rstrip('/')
    return value.removesuffix('.git').lower()


def source_identity(ctx, module):
    if module.source and module.source.get('git'):
        return repository_identity(module.source['git'])
    if module.path:
        try:
            top = Path(git(module.path, 'rev-parse', '--show-toplevel').strip()).resolve()
            if top == module.path.resolve():
                return repository_identity(git(module.path, 'remote', 'get-url', 'origin').strip())
        except Error:
            pass
        for base in (ctx.device, ctx.root, getattr(getattr(ctx, 'soc', None), 'path', None)):
            if base is None or not (base / '.gitmodules').is_file():
                continue
            try:
                relative = str(module.path.relative_to(base))
            except ValueError:
                continue
            try:
                entries = git(base, 'config', '-f', '.gitmodules', '--get-regexp', r'^submodule\..*\.path$')
                for line in entries.splitlines():
                    key, path = line.split(None, 1)
                    if path == relative:
                        return repository_identity(git(base, 'config', '-f', '.gitmodules', '--get', key[:-4] + 'url').strip())
            except Error:
                pass
    return ''


def official_alias(ctx, module, spec):
    repository = repository_identity(spec.get('repository', ''))
    if not repository.startswith('github.com/unixnu/'):
        return False
    legacy = spec.get('legacy_name')
    allowed = {repository}
    if legacy:
        allowed.add('github.com/unixnu/' + legacy.lower())
    return source_identity(ctx, module) in allowed


def resolve(ctx, modules):
    """Select catalog components while retaining explicit device sources."""
    from .feeds import Module
    ctx.component_specs = selected(ctx, modules)
    entries = catalog(ctx)
    result = {key: value for key, value in modules.items()
              if key[0] in ('refer', 'patch', 'package', 'script') or
              (value.origin == 'local (--local-module)' and key[1] not in entries)}
    for spec in ctx.component_specs:
        identifier, kind = spec['id'], spec['kind']
        key = (kind, identifier)
        module = modules.get(key)
        if spec.get('legacy_name'):
            candidate = modules.get((kind, spec['legacy_name']))
            if candidate and official_alias(ctx, candidate, spec) and (module is None or _priority(candidate) < _priority(module)):
                module = candidate
        if module is None:
            path = ctx.root / spec.get('path', f'{kind}s/{identifier}')
            if path.is_dir() and any(path.iterdir()):
                module = Module(kind, identifier, path, 'base')
            else:
                source = {'name': identifier, 'kind': kind, 'git': spec['repository'], 'commit': spec['revision']}
                module = Module(kind, identifier, None, 'git', source)
        if module.name != identifier:
            original = module
            module = Module(kind, identifier, original.path, original.origin, original.source)
            module.commit = original.commit
        module.spec = spec
        result[key] = module
    return result


def _priority(module):
    if module.origin == 'local (--local-module)':
        return 0
    if module.origin.startswith('local (--local-'):
        return 1
    if module.origin == 'local (--local)':
        return 2
    if module.local:
        return 3
    return {'device': 4, 'soc': 5, 'base': 6, 'git': 7}.get(module.origin, 8)


def aliases(ctx, modules):
    """Compatibility names are tied to the official source identity."""
    path = ctx.root / 'components.toml'
    if not path.is_file():
        return []
    result = []
    for spec in catalog(ctx).values():
        legacy = spec.get('legacy_name')
        if not legacy:
            continue
        kind, canonical = spec['kind'], spec['id']
        for name, alias in ((canonical, legacy), (legacy, canonical)):
            module = modules.get((kind, name))
            if module and (kind, alias) not in modules and official_alias(ctx, module, spec):
                result.append((module, alias))
    return result


def sync_outputs(ctx, modules):
    """Link compatibility output paths to the file produced by a build recipe."""
    if not (ctx.root / 'components.toml').is_file():
        return
    for spec in catalog(ctx).values():
        module = modules.get((spec['kind'], spec['id'])) or modules.get((spec['kind'], spec.get('legacy_name')))
        if not module or not official_alias(ctx, module, spec):
            continue
        for alias, canonical in spec.get('legacy_outputs', {}).items():
            paths = [ctx.tree / canonical, ctx.tree / alias]
            candidates = [path for path in paths if path.is_file() and not path.is_symlink()]
            if not candidates:
                continue
            target = max(candidates, key=lambda path: path.stat().st_mtime_ns)
            link = next(path for path in paths if path != target)
            if link.is_dir() and not link.is_symlink():
                continue
            link.parent.mkdir(parents=True, exist_ok=True)
            if link.is_symlink() or link.exists():
                link.unlink()
            link.symlink_to(target)
