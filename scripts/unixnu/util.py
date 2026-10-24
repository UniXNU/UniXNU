"""Small helpers shared by the build driver."""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path


class Error(Exception):
    """A user-facing failure; the command line prints it without a traceback."""


def log(message):
    print(f'== {message}', flush=True)


def expand(path):
    return Path(os.path.expandvars(os.path.expanduser(str(path)))).resolve()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


EXTRA_BIN = ('/opt/homebrew/opt/llvm/bin', '/opt/homebrew/opt/lld/bin', '/usr/local/opt/llvm/bin', '/usr/local/opt/lld/bin')


def tool(name, hint=''):
    """Find a tool on PATH, then in the usual Homebrew LLVM locations (keg-only, not on PATH)."""
    found = shutil.which(name) or shutil.which(name, path=os.pathsep.join(EXTRA_BIN))
    if not found:
        raise Error(f'{name} not found on PATH' + (f' ({hint})' if hint else ''))
    return found


def lzfse():
    """Apple's reference LZFSE tool, which decodes LZFSE on Linux: in the scripts/linux/setup-toolchain.py prefix, else on PATH."""
    path = Path(os.environ.get('UNIXNU_TOOLCHAIN', '/opt/unixnu-linux')) / 'bin/lzfse'
    return str(path) if path.is_file() else tool('lzfse', 'run sudo scripts/linux/setup-toolchain.py')


def run(command, *, cwd=None, env=None, log_file=None, capture=False):
    """Run a command, echoing it. With log_file the output goes there and the tail is shown on failure."""
    command = [str(part) for part in command]
    if not capture:
        print('+ ' + ' '.join(command), flush=True)
    if capture:
        result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
        if result.returncode:
            raise Error(f'{command[0]} failed ({result.returncode}): {result.stderr.strip() or result.stdout.strip()}')
        return result.stdout
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        with Path(log_file).open('w') as stream:
            result = subprocess.run(command, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
        if result.returncode:
            tail = Path(log_file).read_text(errors='replace').splitlines()[-30:]
            print('\n'.join(tail), file=sys.stderr)
            raise Error(f'{command[0]} failed ({result.returncode}); full log: {log_file}')
        return ''
    result = subprocess.run(command, cwd=cwd, env=env)
    if result.returncode:
        raise Error(f'{command[0]} failed ({result.returncode})')
    return ''


def git(repo, *args, capture=True):
    return run(['git', '-C', repo, *args], capture=capture)


CLANGPDB_TOOLS = ('clang', 'lld-link', 'llvm-lib', 'llvm-rc')


def clang_bin(directory):
    """A directory with the tools EDK II's CLANGPDB tool chain expects (CLANG_BIN), linked from wherever they are.

    Apple's clang has no llvm-lib or lld-link, so the Homebrew LLVM and lld are used.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name in CLANGPDB_TOOLS:
        link = directory / name
        target = tool(name, 'brew install llvm lld')
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(target)
    return str(directory) + '/'
