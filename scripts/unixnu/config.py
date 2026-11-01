"""Board, feeds and defconfig files, and the context every build step shares.

A device repository supplies:
  board.toml              board description (like Android BoardConfig.mk)
  configs/<name>_defconfig  CONFIG_* switches (like an OpenWrt defconfig)
  feeds.toml              optional extra sources
  drivers/ kits/ patches/ scripts/ package/   its own modules, same layout as this repository
"""
import json
import os
import re
import tomllib
from pathlib import Path

from .util import Error, expand

ROOT = Path(__file__).resolve().parents[2]
KINDS = {'driver': 'drivers', 'kit': 'kits', 'patch': 'patches', 'script': 'scripts', 'package': 'package', 'refer': 'refer', 'soc': 'socs'}
LOCAL_KINDS = ('drivers', 'kits', 'patches', 'scripts', 'package')


def load_toml(path):
    path = Path(path)
    try:
        return tomllib.loads(path.read_text())
    except FileNotFoundError:
        raise Error(f'missing file: {path}') from None
    except tomllib.TOMLDecodeError as error:
        raise Error(f'{path}: {error}') from None


BUILD_PATHS = {'device', 'out', 'uefi', 'edk2', 'kernelcache', 'kernel',
               'trust_cache', 'owner_trust_cache', 'data_ramdisk', 'gpu_addon',
               'dtb', 'fd', 'ramdisk', 'output'}
BUILD_ENV = {'device': 'UNIXNU_DEVICE', 'out': 'UNIXNU_OUT', 'uefi': 'UNIXNU_UEFI',
             'edk2': 'UNIXNU_EDK2', 'kernelcache': 'UNIXNU_KERNELCACHE',
             'dtb': 'UNIXNU_DTB', 'ipsw': 'UNIXNU_IPSW',
             'unique_chip_id': 'UNIXNU_UNIQUE_CHIP_ID', 'jobs': 'JOBS'}


def load_build_options(args):
    """Apply local build inputs below explicit flags and environment variables."""
    explicit = getattr(args, 'config', None)
    path = expand(explicit) if explicit else ROOT / 'unixnu.local.toml'
    args.build_config = None
    if not explicit and not path.is_file():
        args.target = args.target or 'DEBUG'
        return
    document = load_toml(path)
    if set(document) - {'build'} or not isinstance(document.get('build'), dict):
        raise Error(f'{path}: expected a [build] table')
    options = document['build']
    allowed = BUILD_PATHS | {'ipsw', 'unique_chip_id', 'jobs', 'target', 'kernel_args'}
    for key, value in options.items():
        if key not in allowed:
            raise Error(f'{path}: unknown build option {key}')
        if key == 'kernel_args':
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                raise Error(f'{path}: kernel_args must be an array of strings')
            extra = getattr(args, 'kernel_arg', None) or []
            names = {item.split('=', 1)[0] for item in extra}
            args.kernel_arg = [item for item in value if item.split('=', 1)[0] not in names] + extra
            continue
        if key == 'jobs':
            if type(value) is not int or value < 1:
                raise Error(f'{path}: jobs must be a positive integer')
        elif not isinstance(value, str) or not value:
            raise Error(f'{path}: {key} must be a nonempty string')
        if key == 'target' and value not in ('DEBUG', 'RELEASE'):
            raise Error(f'{path}: target must be DEBUG or RELEASE')
        if getattr(args, key, None) is not None or os.environ.get(BUILD_ENV.get(key, '')):
            continue
        if key in BUILD_PATHS or (key == 'ipsw' and '://' not in value):
            if not (key == 'ramdisk' and value == 'none'):
                local = Path(os.path.expandvars(value)).expanduser()
                value = str((path.parent / local).resolve())
        setattr(args, key, value)
    args.target = args.target or 'DEBUG'
    args.build_config = str(path)


def parse_config(text):
    """Parse a defconfig: CONFIG_X=y, =n, ="text", =123 and "# CONFIG_X is not set"."""
    values = {}
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        unset = re.fullmatch(r'#\s*CONFIG_(\w+) is not set', line)
        if unset:
            values[unset.group(1)] = False
            continue
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'CONFIG_(\w+)=(.*)', line)
        if not match:
            raise Error(f'defconfig line {number} is not CONFIG_NAME=value: {line}')
        name, raw = match.groups()
        if raw == 'y':
            values[name] = True
        elif raw == 'n':
            values[name] = False
        elif raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
            values[name] = raw[1:-1]
        elif re.fullmatch(r'-?(0x[0-9a-fA-F]+|\d+)', raw):
            values[name] = int(raw, 16 if raw.lstrip('-').startswith('0x') else 10)
        else:
            raise Error(f'defconfig line {number}: value must be y, n, a number or a quoted string: {line}')
    return values


class Context:
    """Everything the steps need: repositories, options, board, config and the output layout."""

    def __init__(self, args):
        self.root = ROOT
        load_build_options(args)
        self.args = args
        self.out_root = expand(args.out or os.environ.get('UNIXNU_OUT') or ROOT / 'out')
        self.state_path = self.out_root / 'state.json'
        state = self._load_state()
        device = args.device or os.environ.get('UNIXNU_DEVICE') or state.get('device')
        if not device:
            raise Error('no device repository: pass -D DIR (or set UNIXNU_DEVICE); it is remembered afterwards')
        self.device = expand(device)
        if not (self.device / 'board.toml').is_file():
            raise Error(f'{self.device} has no board.toml')
        self.raw_board = load_toml(self.device / 'board.toml')
        self.schema_version = self.raw_board.get('schema_version', 1)
        if self.schema_version not in (1, 2):
            raise Error(f'unsupported schema_version: {self.schema_version}')
        self.feeds_dir = self.out_root / 'feeds'
        self.lock_path = self.device / 'unixnu.lock'
        self.soc = None
        self.profile_roots = {'device': self.device}
        self.profile_files = [self.device / 'board.toml']
        self.component_specs = []
        self.board = self.raw_board
        if self.schema_version == 2:
            from . import profiles
            self.board = profiles.load(self, allow_fetch=args.command in ('fetch', 'tree', 'build', 'defconfig', 'release'))
        self.name = self.board.get('board', {}).get('name')
        if not self.name:
            raise Error('board.toml needs [board] name')
        self.example = bool(self.board['board'].get('example'))
        if Path(self.name).name != self.name or self.name in ('.', '..'):
            raise Error('[board] name must be a directory name')
        self.work = self.out_root / self.name
        self.config_name = None
        if self.schema_version == 2:
            configurations = state.get('configurations', {})
            selected = (getattr(args, 'name', None) if args.command == 'defconfig' else None)
            from . import profiles
            os_name = profiles.resolve_os(self, args.os) if getattr(args, 'os', None) else self.board['board']['os_profile']
            # [package.defconfig] maps an OS profile to its defconfig; the packaging command always uses it, other commands when --os is given.
            per_os = self.raw_board.get('package', {}).get('defconfig', {}).get(os_name)
            if per_os and (args.command == 'release' or getattr(args, 'os', None)):
                selected = selected or per_os
            else:
                selected = selected or configurations.get(str(self.device))
            selected = selected or per_os or self.board.get('kernel', {}).get('defconfig')
            if not selected or Path(selected).name != selected or selected in ('.', '..'):
                raise Error('schema_version = 2 needs [kernel] defconfig or a selected defconfig')
            self.config_name = selected
            self.work /= os_name
            self.work /= selected.removesuffix('_defconfig')
        self.tree = self.work / 'tree'
        self.logs = self.work / 'logs'
        self.config_path = self.work / '.config'
        self.uefi = None
        self.jobs = args.jobs or int(os.environ.get('JOBS', 0)) or os.cpu_count() or 2
        if args.command != 'status':
            self._save_state({**state, 'device': str(self.device)})
        self.config = parse_config(self.config_path.read_text()) if self.config_path.is_file() else {}

    def remember_config(self, name):
        state = self._load_state()
        configurations = state.setdefault('configurations', {})
        configurations[str(self.device)] = name
        state['device'] = str(self.device)
        self._save_state(state)

    def _load_state(self):
        try:
            return json.loads(self.state_path.read_text())
        except (FileNotFoundError, ValueError):
            return {}

    def _save_state(self, state):
        self.out_root.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2) + '\n')

    def refuse_example(self):
        if self.example:
            raise Error(f'{self.device} is an EXAMPLE device repository (example = true in board.toml); copy it and fill in a real board')

    def need_config(self):
        if not self.config_path.is_file():
            raise Error(f'no configuration: run "unixnu defconfig NAME" first (see {self.device / "configs"})')
        # Re-read: a release writes the configuration at its preflight step, after this context exists.
        self.config = parse_config(self.config_path.read_text())
        return self.config

    def option_text(self, flag, env=None):
        """A string given as a flag or, failing that, an environment variable."""
        return getattr(self.args, flag, None) or (os.environ.get(env) if env else None)

    def option(self, flag, env=None):
        """A path given as a flag or, failing that, an environment variable."""
        value = getattr(self.args, flag, None) or (os.environ.get(env) if env else None)
        return expand(value) if value else None
