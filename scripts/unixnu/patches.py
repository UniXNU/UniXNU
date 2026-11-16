"""Ordered XNU patch series and target-local source preparation."""
import hashlib
import json
import os
import tempfile
import shutil

from pathlib import Path

from .profiles import resolve_path
from .util import Error, git, log, run


def plan(ctx, modules):
    result = []
    for reference in ctx.board.get('kernel', {}).get('patch_series', []):
        series = resolve_path(ctx, reference, modules)
        if not series.is_file():
            raise Error(f'patch series missing: {series}')
        for number, line in enumerate(series.read_text().splitlines(), 1):
            entry = line.strip()
            if not entry or entry.startswith('#'):
                continue
            if entry.startswith('component:') or entry.partition(':')[0] in ctx.profile_roots:
                path = resolve_path(ctx, entry, modules)
            else:
                path = series.parent / entry
            path = path.resolve()
            if not path.is_file():
                raise Error(f'{series}:{number}: patch missing: {path}')
            if path in result:
                raise Error(f'patch appears twice in the selected series: {path}')
            result.append(path)
    return result


def prepare(ctx, modules, env=None):
    selected = plan(ctx, modules)
    module = modules.get(('refer', 'xnu'))
    if not module or module.path is None:
        raise Error('XNU source missing; run unixnu fetch')
    revision = git(module.path, 'rev-parse', 'HEAD').strip()
    signature = {'source': str(module.path), 'commit': revision,
                 'patches': [{'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                             for path in selected]}
    work = ctx.tree / '.cache/xnu-work'
    stamp = ctx.work / 'xnu-inputs.json'
    try:
        previous = json.loads(stamp.read_text())
    except (FileNotFoundError, ValueError):
        previous = None
    if previous != signature or not (work / '.git').is_dir():
        log(f'kernel: prepare XNU {revision[:12]}')
        stamp.unlink(missing_ok=True)
        work.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='xnu-previous-', dir=work.parent) as directory:
            previous = Path(directory) / 'source'
            if work.exists() or work.is_symlink():
                work.rename(previous)
            try:
                run(['git', 'clone', '--quiet', '--shared', '--no-checkout', module.path, work])
                git(work, 'checkout', '--quiet', '--detach', revision)
                for path in selected:
                    log(f'kernel: patch {path.name}')
                    git(work, 'apply', str(path))
                run(['python3', ctx.tree / 'scripts/prepare-xnu-source.py'], cwd=ctx.tree, env=env)
                # Unchanged source and restored headers retain their timestamps,
                # so make can reuse the matching compiled objects.
                for directory, folders, files in os.walk(work):
                    folders[:] = [name for name in folders if name != '.git']
                    for name in files:
                        current = Path(directory) / name
                        old = previous / current.relative_to(work)
                        if current.is_symlink() or old.is_symlink() or not old.is_file():
                            continue
                        stat = old.stat()
                        if current.stat().st_size == stat.st_size and current.read_bytes() == old.read_bytes():
                            os.utime(current, ns=(stat.st_atime_ns, stat.st_mtime_ns))
            except Exception:
                if work.exists():
                    shutil.rmtree(work)
                if previous.exists() or previous.is_symlink():
                    previous.rename(work)
                raise
        stamp.write_text(json.dumps(signature, indent=2) + '\n')
    patch_list = ctx.work / 'xnu-patches.list'
    patch_list.write_text(''.join(str(path) + '\n' for path in selected))
    return patch_list
