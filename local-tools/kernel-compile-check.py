#!/usr/bin/env python3
"""Compile one kernel-side C++ or C source with the flags the build uses, to check it before a full build.

    kernel-compile-check.py SOURCE [--out DIR] [--c] [--record PATH] [-I DIR ...] [--tree TREE]

The flags come from the build tree's XNU compile record (IOPlatformExpert.cpo.json for C++, osfmk startup.o.json for C), with the
warnings build-arm-driver.py and build-gop-legacy-display-27.py add (-Wall -Wextra -Werror and their exceptions). The object goes to
DIR (default: the system temporary directory); prints the result and the undefined and defined global symbols that name 'platform',
'sleep' or 'clamshell', for a quick look at what the object links against.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

WARNINGS = ['-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-Wno-unnecessary-virtual-specifier', '-Wno-c99-designator',
            '-Wno-reorder-init-list', '-Wno-deprecated-enum-enum-conversion']


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--c', action='store_true', help='a C source (osfmk flags)')
    parser.add_argument('--record', help='compile record relative to the XNU object directory')
    parser.add_argument('-I', dest='includes', action='append', default=[])
    parser.add_argument('--tree', type=Path, required=True, help='resolved XNU build tree')
    args = parser.parse_args()
    args.tree = args.tree.resolve()
    obj = args.tree / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837'
    recipe = obj / (args.record or ('osfmk/DEVELOPMENT/startup.o.json' if args.c else 'iokit/DEVELOPMENT/IOPlatformExpert.cpo.json'))
    if not recipe.is_file():
        raise SystemExit(f'{recipe}: no compile record (is the build volume mounted?)')
    record = json.loads(recipe.read_text().strip().rstrip(','))
    out = (args.out or Path(tempfile.gettempdir())).resolve()
    out.mkdir(parents=True, exist_ok=True)
    destination = out / (args.source.stem + '.o')
    command, arguments, index = [], record['arguments'], 0
    while index < len(arguments):
        value = arguments[index]
        if value == record['file']:
            command.append(str(args.source.resolve()))
        elif value == '-o':
            command += ['-o', str(destination)]
            index += 1
        elif value in ('-MF', '-MT', '-MJ'):
            index += 1
        elif value == '-Xclang' and arguments[index + 1].startswith('-W'):
            index += 1
        elif not value.startswith('-W'):
            command.append(value)
        index += 1
    command += WARNINGS + ['-I', str(args.tree / '.cache/xnu-work/osfmk')]
    for include in args.includes:
        command += ['-I', str(Path(include).resolve())]
    result = subprocess.run(command, cwd=record['directory'], capture_output=True, text=True)
    sys.stderr.write(result.stderr[-4000:])
    print(f'{args.source.name}: rc {result.returncode} -> {destination}')
    if result.returncode:
        raise SystemExit(1)
    symbols = subprocess.run(['nm', '-m', str(destination)], capture_output=True, text=True).stdout
    for line in symbols.splitlines():
        if 'external' in line and any(word in line.lower() for word in ('platform', 'sleep', 'clamshell')):
            print('  ' + line.strip())


if __name__ == '__main__':
    main()
