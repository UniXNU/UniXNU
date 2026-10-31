"""One-command packaging of a device: dependencies, patches, build steps, outputs and a manifest.

Every value comes from the device repository's board.toml ([package] and the sections the build steps
already read), the profiles and the local build inputs. Nothing here names a device.
"""
import json
from pathlib import Path

from . import payload
from .util import Error, git, log, sha256_file

MAX_COMMAND_LINE = 1000


def outputs(ctx):
    return {'boot.img': ctx.work / 'boot/boot.img', 'payload.img': payload.paths(ctx)[1], 'kernel.macho': ctx.work / 'kernel/kernel.macho'}


def command_line(ctx):
    """The kernel command line the payload carries, from payload.json written by the payload step."""
    report = payload.paths(ctx)[2]
    if not report.is_file():
        raise Error(f'{report} missing: the payload step did not run')
    return json.loads(report.read_text())['kernel_args']


def write_manifest(ctx, modules, patch_order, files):
    revisions = {}
    for (kind, name), module in sorted(modules.items()):
        revision = module.commit
        if module.path and not revision:
            try:
                revision = git(module.path, 'rev-parse', 'HEAD').strip()
            except Error:
                revision = None
        revisions[f'{kind}:{name}'] = revision
    manifest = {'device': ctx.name, 'os_profile': ctx.work.parent.name, 'configuration': ctx.config_name,
                'revisions': revisions, 'patches': [str(path) for path in patch_order],
                'kernel_command_line_bytes': len(command_line(ctx)),
                'outputs': {name: {'bytes': path.stat().st_size, 'sha256': sha256_file(path)} for name, path in files.items()}}
    target = ctx.work / 'package.manifest.json'
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return target


def verify(ctx, files, manifest):
    recorded = json.loads(manifest.read_text())
    for name, path in files.items():
        if not path.is_file():
            raise Error(f'output missing: {name} ({path})')
        if sha256_file(path) != recorded['outputs'][name]['sha256']:
            raise Error(f'{name} differs from the manifest')
    length = len(command_line(ctx))
    if length >= MAX_COMMAND_LINE:
        raise Error(f'kernel command line is {length} bytes; the limit is {MAX_COMMAND_LINE - 1}')
    partition = ctx.board.get('package', {}).get('boot_partition_bytes')
    size = files['boot.img'].stat().st_size
    if partition and size > partition:
        raise Error(f'boot.img is {size} bytes; the boot partition holds {partition}')
    for name, path in files.items():
        log(f'{name}: {path.stat().st_size} bytes sha256 {sha256_file(path)}')
