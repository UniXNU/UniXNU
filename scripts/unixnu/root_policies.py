"""Bind local verified root headers to the same owner key and block tables."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid

from .util import Error, log, sha256_file


class View(ctypes.Structure):
    _fields_ = [('hashes', ctypes.c_void_p), ('image_bytes', ctypes.c_uint64),
                ('block_count', ctypes.c_uint64), ('generation', ctypes.c_uint64),
                ('volume_uuid', ctypes.c_uint8 * 16), ('image_sha256', ctypes.c_uint8 * 32)]


def validate(directory, digest, identity, library=None, full=False):
    """Validate one previously verified policy without rewriting its evidence."""
    record = json.loads((directory / 'verification.json').read_text())
    key = (directory / 'trusted-key.bin').read_bytes()
    header = ((directory / 'manifest.bin').read_bytes() if full else
              (directory / 'manifest.header.bin').read_bytes())
    blocks = record['blocks_verified']
    if (len(key) != 395 or record.get('real_c_signature_and_block_verification') is not True or
            record.get('original_image_modified') is not False or record['image_sha256'] != digest or
            record['volume_uuid'] != str(uuid.UUID(identity)).upper() or
            record['trusted_key_sha256'] != hashlib.sha256(key).hexdigest() or
            not isinstance(blocks, int) or blocks <= 0 or
            blocks != (record['image_bytes'] + 4095) // 4096 or
            len(header) != (544 + 32 * blocks if full else 544) or header[56:88].hex() != digest):
        raise Error(f'{directory}: root policy, verification record and owner key do not match')
    if full:
        if library is None:
            raise Error('The local VerifiedRoot host verifier is required to reuse local policies')
        encoded, anchor, view = ctypes.create_string_buffer(header), ctypes.create_string_buffer(key), View()
        library.vr_host_open.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p,
                                        ctypes.c_uint64, ctypes.POINTER(View)]
        status = library.vr_host_open(encoded, len(header), anchor, record['generation'], ctypes.byref(view))
        if (status or bytes(view.volume_uuid) != uuid.UUID(identity).bytes or
                bytes(view.image_sha256).hex() != digest or view.image_bytes != record['image_bytes'] or
                view.block_count != blocks or view.generation != record['generation']):
            raise Error(f'{directory}: native policy signature or hash-table authentication failed ({status})')
        if sha256_file(directory / 'hashes.bin') != hashlib.sha256(header[544:]).hexdigest():
            raise Error(f'{directory}: userdata hash table differs from the authenticated policy')
    return {'manifest.header.bin': header[:544], 'trusted-key.bin': key,
            'verification.json': (json.dumps(record, indent=2) + '\n').encode()}


def prepare(ctx):
    """Prefer the installation's local verified policy set over repository fixtures."""
    if not ctx.board.get('payload', {}).get('root_policies') or not ctx.board.get('root'):
        return
    windows = [w['name'] for w in ctx.board.get('userdata', {}).get('windows', [])]
    if not windows:
        return
    build = ctx.tree / 'build'
    local = [build / ('verified-root-' + name) for name in windows]
    use_local = any(path.exists() for path in local)
    library = None
    if use_local:
        verifier = build / 'verified-root-host/verified-root.dylib'
        if not verifier.is_file():
            raise Error(f'Local policy verifier missing: {verifier}')
        library = ctypes.CDLL(str(verifier))
    build_id = ctx.board['ipsw']['build']
    destination = build / ('verified-root-' + build_id)
    shipped = ctx.tree / 'scripts/policies' / ctx.board['board']['os_profile']
    sources = local if use_local else [destination / name if destination.is_dir() else shipped / name for name in windows]
    files, anchors = {}, set()
    try:
        for name, source in zip(windows, sources):
            prefix = name.lower()
            contents = validate(source, ctx.board['root'][prefix + '_image_sha256'],
                                ctx.board['root'][prefix + '_volume_uuid'], library, use_local)
            anchors.add(contents['trusted-key.bin'])
            files.update({Path(name) / entry: data for entry, data in contents.items()})
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise Error(f'Root policy preflight failed: {error}') from error
    if len(anchors) != 1:
        raise Error('Root windows do not share the same installation owner key')
    if use_local and not all((destination / name).is_file() and (destination / name).read_bytes() == data
                             for name, data in files.items()):
        build.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix='root-policy-stage-', dir=build))
        backup = staging.with_name(staging.name + '-previous')
        try:
            candidate = staging / 'candidate'
            for name, data in files.items():
                target = candidate / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            if destination.exists():
                os.replace(destination, backup)
            try:
                os.replace(candidate, destination)
            except BaseException:
                if backup.exists():
                    os.replace(backup, destination)
                raise
            if backup.exists():
                shutil.rmtree(backup)
        finally:
            shutil.rmtree(staging)
    log(f'root policies: {len(windows)} windows - matching owner key, UUIDs and verified image records')
