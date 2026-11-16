#!/usr/bin/env python3
"""Package a source-matched Metal bridge archive and its tracked source files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / 'drivers/AdrenoMetal'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--target', choices=['ios', 'ios27', 'macos27', 'host'], default='macos27')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('choose a new output file')
    source = ROOT / 'build/adreno-metal-bridge' / args.target
    archive = source / 'libadreno_metal_bridge.a'
    metadata = archive.with_suffix('.a.json')
    record = json.loads(metadata.read_text())
    commit = subprocess.check_output(['git', '-C', COMPONENT, 'rev-parse', 'HEAD'], text=True).strip()
    with archive.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if record['identity']['component'] != commit or record['identity']['target'] != args.target or record['sha256'] != digest:
        raise SystemExit('build the bridge for the current component and target before packaging')
    names = subprocess.check_output(['git', '-C', COMPONENT, 'ls-files', '-z']).decode().split('\0')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with args.output.open('xb') as output:
            compressor = subprocess.Popen(['zstd', '-T4', '-3', '-c'], stdin=subprocess.PIPE, stdout=output)
            try:
                with tarfile.open(fileobj=compressor.stdin, mode='w|') as package:
                    package.add(archive, arcname=archive.name)
                    package.add(metadata, arcname=metadata.name)
                    for name in names:
                        if name and (COMPONENT / name).is_file():
                            package.add(COMPONENT / name, arcname='sources/AdrenoMetal/' + name)
                    for name in ('scripts/build-adreno-metal-bridge.py', 'scripts/data/gpu-metal-vulkan-inputs.json'):
                        package.add(ROOT / name, arcname='sources/UniXNU/' + name)
            finally:
                compressor.stdin.close()
            if compressor.wait():
                raise SystemExit('zstd failed')
    except BaseException:
        args.output.unlink(missing_ok=True)
        raise
    print(json.dumps(dict(archive=str(args.output.resolve()), component=commit,
                          runtime=record['identity']['runtime'], bytes=args.output.stat().st_size)))


if __name__ == '__main__':
    main()
