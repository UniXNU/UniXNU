"""Prepare reproducible runtime inputs before compiling the kernel.

The board supplies a builder. An existing Data seed is immutable: generating a
replacement is an explicit first-install operation, never a cache-miss fallback.
"""
import importlib.util
import json
import os
import re
import sys
import uuid
from pathlib import Path

from .ipsw import Ipsw
from .util import Error, log, run, sha256_file


def seed_uuid(tree, path):
    spec = importlib.util.spec_from_file_location('runtime_packed_ramdisk', tree / 'drivers/DarwinBoot/Test/packed_ramdisk.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _, extents = module.regions(path.read_bytes())
    identities = set()
    for _, data in extents:
        for at in range(0, len(data), 4096):
            block = data[at:at + 4096]
            if block[32:36] == b'APSB':
                identities.add(str(uuid.UUID(bytes=bytes(block[240:256]))).upper())
    if len(identities) != 1:
        raise Error(f'{path}: require a packed APFS seed with exactly one volume UUID')
    return identities.pop()


def prepare(ctx, kernel_build=False):
    spec = ctx.board.get('payload', {}).get('runtime')
    if not spec or not spec.get('enabled', True):
        from .payload import check_data_input
        check_data_input(ctx, getattr(ctx.args, 'data_ramdisk', None))
        return
    if getattr(ctx, '_runtime_prepared', False):
        return
    args = ctx.args
    out = ctx.work / 'runtime'
    out.mkdir(parents=True, exist_ok=True)
    seed = Path(args.data_ramdisk).expanduser().resolve() if args.data_ramdisk else out / 'data.dbr'
    init = bool(getattr(args, 'init_data', False))
    if init and args.data_ramdisk:
        raise Error('--init-data cannot replace --data-ramdisk; use one first-install seed or reuse the original')
    if init and not kernel_build:
        raise Error('--init-data needs a kernel build to bind its new Data volume UUID')
    if not seed.is_file() and not init:
        raise Error('No preserved Data seed. Pass --data-ramdisk FILE for an existing installation, '
                    'or --init-data for a FIRST installation; a missing cache never regenerates Data automatically')
    previous = out / 'inputs.json'
    if not args.data_ramdisk and seed.is_file() and previous.is_file():
        expected = json.loads(previous.read_text())['inputs']['data_ramdisk']['sha256']
        if sha256_file(seed) != expected:
            raise Error('Saved Data seed differs from its recorded SHA-256; restore the original installation seed')
    owner = getattr(args, 'owner_trust_cache', None)
    trust = owner or getattr(args, 'trust_cache', None)
    addon = getattr(args, 'gpu_addon', None)
    for name, path in [('Data seed', args.data_ramdisk), ('trust bundle', trust), ('GPU addon', addon)]:
        if path and not Path(path).expanduser().is_file():
            raise Error(f'{name} not found: {path}')
    # Preserve explicit inputs. A source-built addon must be paired with newly
    # collected CDHashes, so an explicit trust bundle alone is not sufficient.
    if trust and not addon:
        raise Error('Pass both --gpu-addon and its --owner-trust-cache, or omit both to build them from source')
    request = dict(spec, tree=str(ctx.tree), device=str(ctx.device), output=str(out),
                   data_ramdisk=str(seed), init_data=init,
                   gpu_addon=str(Path(addon).expanduser().resolve()) if addon else None,
                   trust_cache=str(Path(trust).expanduser().resolve()) if trust else None)
    if not seed.is_file() or not trust or not addon:
        source = Ipsw(ctx)
        if not seed.is_file() or not addon:
            request['os_image'] = str(source.disk_image('OS'))
        if not trust:
            request['trust_modules'] = [str(source.extract(name)) for name in spec['trust_components']]
        request_path = out / 'request.json'
        request_path.write_text(json.dumps(request, indent=2) + '\n')
        report = out / 'generated.json'
        report.unlink(missing_ok=True)
        run([sys.executable, ctx.tree / spec['tool'], '--request', request_path], cwd=ctx.tree,
            env=dict(os.environ, UNIXNU_DEVICE=str(ctx.device)), log_file=ctx.logs / 'runtime.log')
        if not report.is_file():
            raise Error('runtime builder did not produce generated.json')
        generated = json.loads(report.read_text())
        seed = Path(generated['data_ramdisk'])
        trust, addon = generated['trust_cache'], generated['gpu_addon']
        owner = trust
    identity = seed_uuid(ctx.tree, seed)
    config = ctx.need_config()
    if identity != config.get('XNU_OWNER_DATA_VOLUME_UUID'):
        if not kernel_build:
            raise Error('Data seed UUID differs from the compiled configuration; rebuild the kernel with this seed')
        text = ctx.config_path.read_text()
        text, count = re.subn(r'^CONFIG_XNU_OWNER_DATA_VOLUME_UUID=.*$',
                             f'CONFIG_XNU_OWNER_DATA_VOLUME_UUID="{identity}"', text, flags=re.M)
        if count != 1:
            raise Error('runtime Data requires exactly one CONFIG_XNU_OWNER_DATA_VOLUME_UUID')
        ctx.config_path.write_text(text)
        ctx.need_config()
    args.data_ramdisk, args.gpu_addon = str(seed), str(addon)
    if owner:
        args.owner_trust_cache = str(trust)
    else:
        args.trust_cache = str(trust)
    inputs = {name: {'path': str(path), 'sha256': sha256_file(Path(path))}
              for name, path in [('data_ramdisk', seed), ('trust_cache', trust), ('gpu_addon', addon)]}
    (out / 'inputs.json').write_text(json.dumps(dict(inputs=inputs, data_volume_uuid=identity), indent=2) + '\n')
    log(f'runtime: Data UUID {identity}; preserved seed sha256 {inputs["data_ramdisk"]["sha256"]}')
    ctx._runtime_prepared = True
