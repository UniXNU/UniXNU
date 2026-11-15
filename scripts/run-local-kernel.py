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
    if not (args.sdk / 'SDKSettings.plist').exists() or not all((args.tools / name).is_file() for name in ('migcom', 'iig')):
        parser.error('require the exported SDK and migcom/iig tools')
    for name in ('migcom', 'iig'):
        (args.tools / name).chmod(0o755)
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
if '--find' in args or '-find' in args:
    name=args[-1]
    if name in ('migcom','iig'):
        print(os.path.join(os.environ['UNIXNU_LOCAL_TOOLS'],name));sys.exit(0)
os.execv('/usr/bin/xcrun',['/usr/bin/xcrun']+args)
''')
        wrapper.chmod(0o755)
        environment = dict(os.environ, UNIXNU_LOCAL_SDK=str(args.sdk.resolve()),
                           UNIXNU_LOCAL_TOOLS=str(args.tools.resolve()), XNU_SDKROOT=str(args.sdk.resolve()),
                           MIGCOM=str((args.tools / 'migcom').resolve()), IIG=str((args.tools / 'iig').resolve()),
                           PLATFORM='iPhoneOS', DYLD_LIBRARY_PATH='/Library/Developer/CommandLineTools/usr/lib')
        environment['PATH'] = directory + os.pathsep + environment.get('PATH', '')
        subprocess.run([str(ROOT / 'unixnu'), *arguments], env=environment, cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
