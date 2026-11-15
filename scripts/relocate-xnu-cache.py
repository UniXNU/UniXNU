#!/usr/bin/env python3
"""Relocate an exported XNU build cache to a local resolved tree and SDK."""
import argparse
import json
import os
from pathlib import Path

CORE = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tree', type=Path)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--device', type=Path, required=True)
    parser.add_argument('--toolchain', type=Path, required=True, help='exported toolchain usr directory')
    args = parser.parse_args()
    tree = args.tree.resolve()
    record = json.loads(args.metadata.read_text())
    old_core, separator, _ = record['tree'].partition('/out/')
    if not separator:
        parser.error('exported tree must belong to a UniXNU out directory')
    old_developer = record['sdk'].split('/Platforms/', 1)[0]
    toolchain = str(args.toolchain.resolve())
    replacements = [(record['tree'], str(tree)), (record['sdk'], str(args.sdk.resolve())),
                    (record.get('toolchain', old_developer + '/Toolchains/XcodeDefault.xctoolchain/usr'), toolchain),
                    ('/Library/Developer/CommandLineTools/usr', toolchain),
                    (str(Path(old_core).parent / 'device'), str(args.device.resolve())), (old_core, str(CORE))]

    def relocate(text):
        for before, after in replacements:
            text = text.replace(before, after)
        return text

    changed = 0
    for root in (tree / '.cache/xnu-work', tree / '.cache/fakeroot', tree / 'build/xnu'):
        for path in root.rglob('*'):
            if path.is_symlink():
                target = os.readlink(path)
                replacement = relocate(target)
                if target != replacement:
                    path.unlink()
                    path.symlink_to(replacement)
                    changed += 1
                continue
            if not path.is_file() or path.stat().st_size > 8 * 1024 * 1024:
                continue
            with path.open('rb') as stream:
                prefix = stream.read(4096)
                if b'\0' in prefix:
                    continue
                data = prefix + stream.read()
            text = data.decode('utf-8', errors='surrogateescape')
            replacement = relocate(text)
            if text != replacement:
                stat = path.stat()
                path.write_bytes(replacement.encode('utf-8', errors='surrogateescape'))
                os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
                changed += 1
    print(f'Relocated {changed} cached build files and symlinks.')


if __name__ == '__main__':
    main()
