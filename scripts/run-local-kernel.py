#!/usr/bin/env python3
"""Build a kernel locally with an exported iPhoneOS SDK and kernel tools."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--tools', type=Path, required=True)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    required = ('clang', 'clang++', 'ld', 'ld-classic', 'migcom', 'iig')
    if not (args.sdk / 'SDKSettings.plist').exists() or not all((args.tools / name).is_file() for name in required):
        parser.error('require the exported SDK, compiler, linker and kernel tools')
    for tool in args.tools.iterdir():
        if tool.is_file():
            tool.chmod(0o755)
    libraries = args.tools.resolve().parent / 'lib'
    clang_library = libraries / 'libclang.dylib'
    if not clang_library.is_file():
        parser.error('require the exported toolchain lib/libclang.dylib')
    arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
    if not arguments:
        parser.error('pass unixnu build arguments after --')
    with tempfile.TemporaryDirectory(prefix='unixnu-kernel-tools-') as directory:
        wrapper = Path(directory) / 'xcrun'
        wrapper.write_text('''#!/usr/bin/env python3
import os,sys
args=sys.argv[1:]
for i,value in enumerate(args[:-1]):
    if value in ('--sdk','-sdk') and args[i+1]=='iphoneos':
        args[i+1]=os.environ['UNIXNU_LOCAL_SDK']
if any(value in args for value in ('--find','-find','-f')):
    name=args[-1]
    tool=os.path.join(os.environ['UNIXNU_LOCAL_TOOLS'],name)
    if os.path.isfile(tool):
        print(tool);sys.exit(0)
i=0
while i<len(args):
    value=args[i]
    if value in ('--sdk','-sdk','--toolchain','-toolchain'):
        i+=2;continue
    if value.startswith('-'):
        i+=1;continue
    tool=os.path.join(os.environ['UNIXNU_LOCAL_TOOLS'],value)
    if os.path.isfile(tool):
        os.execv(tool,[tool]+args[i+1:])
    break
os.execv('/usr/bin/xcrun',['/usr/bin/xcrun']+args)
''')
        wrapper.chmod(0o755)
        environment = dict(os.environ, UNIXNU_LOCAL_SDK=str(args.sdk.resolve()),
                           UNIXNU_LOCAL_TOOLS=str(args.tools.resolve()), XNU_SDKROOT=str(args.sdk.resolve()),
                           MIGCOM=str((args.tools / 'migcom').resolve()), IIG=str((args.tools / 'iig').resolve()),
                           PLATFORM='iPhoneOS', DYLD_LIBRARY_PATH=str(libraries))
        environment['PATH'] = directory + os.pathsep + str(args.tools.resolve()) + os.pathsep + environment.get('PATH', '')
        subprocess.run([str(ROOT / 'unixnu'), *arguments], env=environment, cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
