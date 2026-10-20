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
KINDS = {'driver': 'drivers', 'kit': 'kits', 'patch': 'patches', 'script': 'scripts', 'package': 'package', 'refer': 'refer'}
LOCAL_KINDS = ('drivers', 'kits', 'patches', 'scripts', 'package')


def load_toml(path):
    path = Path(path)
    try:
        return tomllib.loads(path.read_text())
    except FileNotFoundError:
        raise Error(f'missing file: {path}') from None
    except tomllib.TOMLDecodeError as error:
        raise Error(f'{path}: {error}') from None


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
        self.board = load_toml(self.device / 'board.toml')
        self.name = self.board.get('board', {}).get('name')
        if not self.name:
            raise Error('board.toml needs [board] name')
        self.example = bool(self.board['board'].get('example'))
        self.work = self.out_root / self.name
        self.tree = self.work / 'tree'
        self.logs = self.work / 'logs'
        self.feeds_dir = self.out_root / 'feeds'
        self.config_path = self.work / '.config'
        self.uefi = None
        self.jobs = args.jobs or int(os.environ.get('JOBS', 0)) or os.cpu_count() or 2
        self._save_state({'device': str(self.device)})
        self.config = parse_config(self.config_path.read_text()) if self.config_path.is_file() else {}
        self.lock_path = self.device / 'unixnu.lock'

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
        return self.config

    def option_text(self, flag, env=None):
        """A string given as a flag or, failing that, an environment variable."""
        return getattr(self.args, flag, None) or (os.environ.get(env) if env else None)

    def option(self, flag, env=None):
        """A path given as a flag or, failing that, an environment variable."""
        value = getattr(self.args, flag, None) or (os.environ.get(env) if env else None)
        return expand(value) if value else None
