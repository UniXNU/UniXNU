"""Android boot image: gzip(BootShim + UEFI FD) with the device tree appended, plus an optional ramdisk.

Inputs are a Mu-Silicium checkout (BootShim sources, Resources/Configs/<device>.toml, mkbootimg.py),
the built firmware volume and a compiled device tree. The image is meant for "fastboot boot" only.
The result is verified by unpacking it again; the output is deterministic.
"""
import gzip
import hashlib
import json
import shutil
import struct
import tempfile
import zlib
from pathlib import Path

from .config import load_toml
from .util import Error, log, run, sha256_file, tool

DEFAULTS = {'header_version': 0, 'base': 0, 'kernel_offset': 0x8000, 'tags_offset': 0x1e00000, 'pagesize': 4096}
MKBOOTIMG_FLAGS = ('base', 'kernel_offset', 'tags_offset', 'pagesize', 'header_version', 'ramdisk_offset', 'second_offset', 'cmdline')


def compile_shim(uefi, base, size, requires_header, scratch):
    clang, objcopy, nm = tool('clang'), tool('llvm-objcopy', 'brew install llvm'), tool('llvm-nm', 'brew install llvm')
    source = uefi / 'BootShim/BootShim.S'
    if not source.is_file():
        raise Error(f'{source} missing: --uefi must be a Mu-Silicium checkout')
    obj = scratch / 'shim.o'
    run([clang, '--target=aarch64-none-elf', '-c', f'-DFD_BASE={base}', f'-DFD_SIZE={size}',
         f'-DREQUIRES_KERNEL_HEADER={int(requires_header)}', source, '-o', obj], capture=True)
    run([objcopy, '-O', 'binary', obj, scratch / 'shim.bin'], capture=True)
    shim = (scratch / 'shim.bin').read_bytes()
    symbols = run([nm, '-n', obj], capture=True)
    offset = next((int(line.split()[0], 16) for line in symbols.splitlines() if line.endswith(' _Payload')), None)
    if offset != len(shim):
        raise Error('a literal pool or padding separates the _Payload label from the appended firmware volume')
    if requires_header and (shim[56:60] != b'ARM\x64' or struct.unpack_from('<QQ', shim, 8) != (base, len(shim) + size)):
        raise Error('the ARM64 image header does not describe the shim plus the firmware volume')
    return shim


def patch_dtb(dtb, nodes, scratch):
    """Add device-tree nodes the stock bootloader expects (board.toml [[bootimg.dtb_node]])."""
    if not nodes:
        return dtb
    fdtput, fdtget = tool('fdtput', 'brew install dtc'), tool('fdtget', 'brew install dtc')
    work = scratch / 'device.dtb'
    work.write_bytes(dtb)
    for node in nodes:
        run([fdtput, '-c', work, node['path']], capture=True)
        for prop in node.get('props', []):
            values = prop['value'] if isinstance(prop['value'], list) else [prop['value']]
            run([fdtput, '-t', prop.get('type', 's'), work, node['path'], prop['name'], *[str(v) for v in values]], capture=True)
            got = run([fdtget, '-t', prop.get('type', 's'), work, node['path'], prop['name']], capture=True).split()
            kind = prop.get('type', 's')
            if kind in ('x', 'i', 'u') and [int(v, 16 if kind == 'x' else 10) for v in got] != [int(str(v), 0) for v in values]:
                raise Error(f'dtb node {node["path"]} property {prop["name"]} did not round-trip')
    return work.read_bytes()


def settings(ctx, uefi):
    fw = ctx.board.get('firmware', {})
    config = load_toml(uefi / 'Resources/Configs' / f'{fw["config"]}.toml') if fw.get('config') else {}
    values = dict(DEFAULTS)
    values.update(config.get('boot_image', {}))
    values.update(ctx.board.get('bootimg', {}).get('image', {}))
    fd = config.get('uefi_fd', {})
    return values, fd.get('base'), fd.get('size'), config.get('boot_shim', {}).get('requires_kernel_header', True), config


def build(ctx, uefi, fd, dtb, ramdisk=None, output=None):
    log('bootimg')
    image, base, size, requires_header, config = settings(ctx, uefi)
    mkbootimg = uefi / 'Resources/Scripts/mkbootimg.py'
    if not mkbootimg.is_file():
        raise Error(f'{mkbootimg} missing: --uefi must be a Mu-Silicium checkout')
    for path, what in ((fd, 'firmware volume (--fd)'), (dtb, 'device tree (--dtb)')):
        if not path or not Path(path).is_file():
            if path == fd:
                raise Error(f'firmware volume not found: {fd}; run ./unixnu build firmware --uefi {uefi}')
            raise Error(f'{what} not found: {path}')
    firmware = Path(fd).read_bytes()
    if base is None or size is None:
        raise Error('the Mu-Silicium device config has no [uefi_fd] base and size')
    if len(firmware) != size:
        raise Error(f'firmware volume is {len(firmware):#x} bytes, the device config says {size:#x}')
    out = Path(output) if output else ctx.work / 'boot/boot.img'
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='unixnu-bootimg-') as scratch_name:
        scratch = Path(scratch_name)
        shim = compile_shim(uefi, base, size, requires_header, scratch)
        tree = patch_dtb(Path(dtb).read_bytes(), ctx.board.get('bootimg', {}).get('dtb_node', []), scratch)
        if tree[:4] != b'\xd0\x0d\xfe\xed' or struct.unpack_from('>I', tree, 4)[0] != len(tree):
            raise Error('invalid compiled device tree')
        combined = shim + firmware
        kernel = gzip.compress(combined, mtime=0) + tree
        kernel_path = scratch / 'Image.gz-dtb'
        kernel_path.write_bytes(kernel)
        if ramdisk:
            ramdisk_path = Path(ramdisk)
            if not ramdisk_path.is_file():
                raise Error(f'ramdisk not found: {ramdisk_path}')
        else:
            ramdisk_path = scratch / 'ramdisk'
            ramdisk_path.write_bytes(b'')
        command = ['python3', mkbootimg, '--kernel', kernel_path, '--ramdisk', ramdisk_path, '-o', out]
        for key in MKBOOTIMG_FLAGS:
            if key in image:
                command += [f'--{key}', str(image[key])]
        run(command, capture=True)
        report = verify(out, combined, tree, ramdisk_path, image)
    report.update(image_sha256=sha256_file(out), image_bytes=out.stat().st_size, fd_sha256=sha256_file(fd),
                  dtb_sha256=sha256_file(dtb), shim_bytes=len(shim), hardware_tested=False)
    (out.parent / 'boot.json').write_text(json.dumps(report, indent=2) + '\n')
    log(f'bootimg: {out} ({out.stat().st_size} bytes)')
    return out


def verify(path, combined, tree, ramdisk_path, image):
    """Unpack the image and compare every part with its input."""
    data = Path(path).read_bytes()
    if data[:8] != b'ANDROID!':
        raise Error('boot image magic missing')
    # header_version sits at offset 40 in both the v0 and the v3/v4 layouts.
    version = struct.unpack_from('<I', data, 40)[0]
    if version != image['header_version']:
        raise Error('boot image header does not match the requested parameters')
    page = image['pagesize']
    if version >= 3:
        # v3/v4 drop the load addresses and the second stage: the kernel follows a
        # header_size-padded header and the ramdisk follows the kernel.
        kernel_size, ramdisk_size, _os_version, header_size = struct.unpack_from('<4I', data, 8)
        kernel_address = tags = 0
        start = page * max(1, -(-header_size // page))
        ramdisk_start = start + page * (-(-kernel_size // page))
    else:
        kernel_size, kernel_address, ramdisk_size, _, second_size, _, tags, header_page, _, _ = struct.unpack_from('<10I', data, 8)
        if second_size or header_page != page:
            raise Error('boot image header does not match the requested parameters')
        if kernel_address != image['base'] + image['kernel_offset'] or tags != image['base'] + image['tags_offset']:
            raise Error('boot image load addresses do not match the requested offsets')
        start = 0
        ramdisk_start = page * (1 + -(-kernel_size // page))
    kernel = data[start:start + kernel_size]
    unpacker = zlib.decompressobj(16 + zlib.MAX_WBITS)
    if unpacker.decompress(kernel) != combined or not unpacker.eof or unpacker.unused_data != tree:
        raise Error('gzip, firmware and appended device tree do not round-trip')
    if data[ramdisk_start:ramdisk_start + ramdisk_size] != Path(ramdisk_path).read_bytes():
        raise Error('ramdisk bytes differ')
    return {'kernel_sha256': hashlib.sha256(kernel).hexdigest(), 'ramdisk_bytes': ramdisk_size,
            'header_version': version, 'kernel_address': hex(kernel_address), 'tags_address': hex(tags)}
