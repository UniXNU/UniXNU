#!/usr/bin/env python3
"""Copy a GPU addon (NGPUADD2, see UniXNU scripts/make-gpu-addon.py) and add the files of DIR below PREFIX.
usage: addon-add-dir.py IN.bin OUT.bin PREFIX DIR [PREFIX DIR ...] [--addon FILE]
Executables keep 0755, the rest 0644. --addon merges entries from another addon."""
import os
import struct
import sys
import zlib
from pathlib import Path


def pad(b):
    return b + bytes(-len(b) % 8)


def read(path):
    data = Path(path).read_bytes()
    assert data[:8] == b'NGPUADD2', 'not an addon'
    count = struct.unpack_from('<I', data, 8)[0]
    at, files = 24, []
    for _ in range(count):
        plen, mode, size, packed = struct.unpack_from('<IIQQ', data, at)
        at += 24
        name = data[at:at + plen - 1].decode()
        at += (plen + 7) & ~7
        body = zlib.decompress(data[at:at + packed])
        assert len(body) == size
        at += (packed + 7) & ~7
        files.append((name, mode, body))
    return files


def write(path, files):
    out = b''
    for name, mode, body in files:
        raw = name.encode() + b'\0'
        assert len(raw) <= 160, name
        packed = zlib.compress(body, 9)
        out += struct.pack('<IIQQ', len(raw), mode, len(body), len(packed)) + pad(raw) + pad(packed)
    blob = b'NGPUADD2' + struct.pack('<IIQ', len(files), 0, 24 + len(out)) + out
    Path(path).write_bytes(blob)


def main():
    if len(sys.argv) < 5 or len(sys.argv) % 2 == 0:
        sys.exit(__doc__)
    files = read(sys.argv[1])
    for prefix, directory in zip(sys.argv[3::2], sys.argv[4::2]):
        if prefix == '--addon':
            for entry in read(directory):
                files = [item for item in files if item[0] != entry[0]] + [entry]
            continue
        base = Path(directory)
        if prefix.startswith('--') or not base.is_dir():
            sys.exit('Expected a directory for addon prefix ' + prefix + ': ' + directory)
        for p in sorted(x for x in base.rglob('*') if x.is_file()):
            name = prefix.rstrip('/') + '/' + p.relative_to(base).as_posix()
            mode = 0o755 if os.access(p, os.X_OK) else 0o644
            files = [f for f in files if f[0] != name] + [(name, mode, p.read_bytes())]
    write(sys.argv[2], files)
    assert [f[0] for f in read(sys.argv[2])] == [f[0] for f in files]
    print(f'{sys.argv[2]}: {len(files)} files')


if __name__ == '__main__':
    main()
