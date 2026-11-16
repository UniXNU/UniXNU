"""Select an exported Apple toolchain for the kernel build and prelink steps."""
from contextlib import contextmanager
import os
from pathlib import Path
import tempfile

from .util import Error


@contextmanager
def environment(ctx):
    sdk = ctx.option('kernel_sdk', 'UNIXNU_KERNEL_SDK')
    tools = ctx.option('kernel_tools', 'UNIXNU_KERNEL_TOOLS')
    if sdk is None and tools is None:
        yield
        return
    required = ('clang', 'clang++', 'ld', 'ld-classic', 'migcom', 'iig')
    if sdk is None or tools is None or not (sdk / 'SDKSettings.plist').is_file() or not all((tools / name).is_file() for name in required):
        raise Error('pass --kernel-sdk SDK and --kernel-tools TOOLCHAIN/bin with the exported compiler, linker and kernel tools')
    libraries = tools.resolve().parent / 'lib'
    if not (libraries / 'libclang.dylib').is_file():
        raise Error('the exported toolchain needs lib/libclang.dylib')
    for tool in tools.iterdir():
        if tool.is_file():
            tool.chmod(tool.stat().st_mode | 0o111)
    with tempfile.TemporaryDirectory(prefix='unixnu-kernel-tools-') as directory:
        executable = Path(directory) / 'xcrun'
        executable.write_text('''#!/usr/bin/env python3
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
        executable.chmod(0o755)
        selected = dict(UNIXNU_LOCAL_SDK=str(sdk), UNIXNU_LOCAL_TOOLS=str(tools),
                        XNU_SDKROOT=str(sdk), MIGCOM=str(tools / 'migcom'), IIG=str(tools / 'iig'),
                        PLATFORM='iPhoneOS', DYLD_LIBRARY_PATH=str(libraries),
                        PATH=directory + os.pathsep + str(tools) + os.pathsep + os.environ.get('PATH', ''))
        previous = {key: os.environ.get(key) for key in selected}
        os.environ.update(selected)
        try:
            yield
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
