"""Ordered XNU patch series and target-local source preparation."""
import hashlib
import json
import os
import shutil

from .profiles import resolve_path
from .util import Error, git, log, run


def keep_unchanged_times(old, new):
    """Give each file of `new` that is byte-identical to its counterpart in `old` the old times.

    A fresh clone stamps every file with the clone time, which makes the next make rebuild all of
    XNU. Files a patch changed keep the new time, so their dependents still rebuild.
    """
    kept = 0
    for path in new.rglob('*'):
        relative = path.relative_to(new)
        if relative.parts[0] == '.git' or path.is_symlink() or not path.is_file():
            continue
        before = old / relative
        try:
            status = before.stat()
        except FileNotFoundError:
            continue
        if before.is_symlink() or status.st_size != path.stat().st_size:
            continue
        if before.read_bytes() == path.read_bytes():
            os.utime(path, ns=(status.st_atime_ns, status.st_mtime_ns))
            kept += 1
    return kept


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


def prepare(ctx, modules):
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
        # Keep the old tree until the new one is ready, so files whose bytes did not change keep their
        # modification times and make rebuilds only what a patch touched instead of the whole kernel.
        previous_tree = work.with_name(work.name + '.previous')
        if previous_tree.exists():
            shutil.rmtree(previous_tree)
        if work.exists():
            work.rename(previous_tree)
        work.parent.mkdir(parents=True, exist_ok=True)
        run(['git', 'clone', '--quiet', '--shared', '--no-checkout', module.path, work])
        git(work, 'checkout', '--quiet', '--detach', revision)
        for path in selected:
            log(f'kernel: patch {path.name}')
            try:
                git(work, 'apply', str(path))
            except Error as error:
                shutil.rmtree(work)
                raise Error(f'XNU patch {path}: {error}') from error
        # A fresh clone lacks the public headers newer xnu omits (TrustCache among them); archives compile against it before the kernel build.
        run(['python3', ctx.tree / 'scripts/prepare-xnu-source.py'], cwd=ctx.tree)
        if previous_tree.exists():
            kept = keep_unchanged_times(previous_tree, work)
            log(f'kernel: {kept} unchanged XNU files keep their times')
            shutil.rmtree(previous_tree)
        stamp.write_text(json.dumps(signature, indent=2) + '\n')
    patch_list = ctx.work / 'xnu-patches.list'
    patch_list.write_text(''.join(str(path) + '\n' for path in selected))
    return patch_list
