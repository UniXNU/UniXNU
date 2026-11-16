"""Sector-addressable FAT images with independently compressed UEFI chunks."""
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

MAGIC = b'UNXNFAT1'
CHUNK = 1024 * 1024
HEADER = struct.Struct('<8sQII')
ENTRY = struct.Struct('<II')
ROOT = Path(__file__).resolve().parents[2]


def compressor(*roots):
    found = shutil.which('TianoCompress')
    candidates = [Path(found)] if found else []
    for root in (*roots, ROOT):
        root = Path(root)
        candidates += [root / 'BaseTools/Source/C/bin/TianoCompress',
                       root / 'Common/Mu/BaseTools/Source/C/bin/TianoCompress',
                       root / 'refer/edk2/BaseTools/Source/C/bin/TianoCompress']
        candidates += sorted(root.glob('out/feeds/mu_basecore-*/BaseTools/Source/C/bin/TianoCompress'))
    for path in candidates:
        if path.is_file():
            return path.resolve()
    raise FileNotFoundError('Build the selected EDK II BaseTools to provide TianoCompress')


def packed(path):
    with Path(path).open('rb') as stream:
        return stream.read(8) == MAGIC


def encode(source, output, *roots):
    source, output = Path(source), Path(output)
    size = source.stat().st_size
    if not size or size % 512 or size > 1024**3:
        raise ValueError('FAT size must be sector-aligned and at most 1 GiB')
    if source.resolve() == output.resolve():
        raise ValueError('Use separate source and output files')
    tool = compressor(*roots)
    count = (size + CHUNK - 1) // CHUNK
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='unixnu-ramdisk-', dir=output.parent) as directory:
        work = Path(directory)
        entries = []
        with source.open('rb') as incoming, (work / 'result').open('wb') as result:
            result.write(HEADER.pack(MAGIC, size, CHUNK, count))
            result.write(bytes(ENTRY.size * count))
            while data := incoming.read(CHUNK):
                (work / 'chunk').write_bytes(data)
                subprocess.run([str(tool), '-e', '--uefi', '-q', '-o', str(work / 'compressed'),
                                str(work / 'chunk')], check=True, capture_output=True)
                compressed = (work / 'compressed').read_bytes()
                entries.append((result.tell(), len(compressed)))
                result.write(compressed)
                result.write(bytes(-result.tell() % 8))
            result.seek(HEADER.size)
            for entry in entries:
                result.write(ENTRY.pack(*entry))
        (work / 'result').replace(output)


def decode(source, output, *roots):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError('Use separate source and output files')
    if not packed(source):
        shutil.copyfile(source, output)
        return
    tool = compressor(*roots)
    with source.open('rb') as incoming:
        magic, size, chunk, count = HEADER.unpack(incoming.read(HEADER.size))
        if chunk != CHUNK or not size or size % 512 or size > 1024**3 or count != (size + chunk - 1) // chunk:
            raise ValueError('Invalid compressed FAT geometry')
        table = [ENTRY.unpack(incoming.read(ENTRY.size)) for _ in range(count)]
        source_size = source.stat().st_size
        with tempfile.TemporaryDirectory(prefix='unixnu-ramdisk-', dir=output.parent) as directory:
            work = Path(directory)
            with (work / 'result').open('wb') as result:
                for index, (offset, length) in enumerate(table):
                    if offset < HEADER.size + count * ENTRY.size or length < 8 or offset + length > source_size:
                        raise ValueError('Compressed FAT chunk exceeds its input')
                    incoming.seek(offset)
                    (work / 'compressed').write_bytes(incoming.read(length))
                    subprocess.run([str(tool), '-d', '--uefi', '-q', '-o', str(work / 'chunk'),
                                    str(work / 'compressed')], check=True, capture_output=True)
                    data = (work / 'chunk').read_bytes()
                    if len(data) != min(chunk, size - index * chunk):
                        raise ValueError('Decoded FAT chunk has an invalid length')
                    result.write(data)
            (work / 'result').replace(output)
