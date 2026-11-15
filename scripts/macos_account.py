"""Shared administrator input for macOS Data seed tools."""
import contextlib
import getpass
import json
import os
import re
import sys


def add_account_arguments(parser):
    account = parser.add_mutually_exclusive_group()
    account.add_argument('--user', metavar='NAME:PASSWORD', help='local administrator short name and password')
    account.add_argument('--user-stdin', action='store_true',
                         help='read administrator name and password from JSON on standard input')
    account.add_argument('--interactive-user', action='store_true',
                         help='prompt for administrator short name, display name and password')
    parser.add_argument('--real-name', help='administrator display name (default: short name)')


def read_account(parser, args):
    """Resolve exactly one input mode without opening a terminal for supplied credentials."""
    if getattr(args, 'interactive_user', False):
        try:
            name, args.real_name, password = prompt_account(
                real_name=args.real_name, skip_setup=getattr(args, 'skip_setup', False),
                auto_login=getattr(args, 'auto_login', False))
        except (OSError, RuntimeError, EOFError, ValueError) as error:
            parser.error(str(error) or 'account input was interrupted')
        args.user = name + ':' + password
    elif args.user_stdin:
        try:
            record = json.load(sys.stdin)
            name, password = record['name'], record['password']
            if not isinstance(name, str) or not isinstance(password, str) or ':' in name:
                raise ValueError('invalid account fields')
            if args.real_name is None and 'real_name' in record:
                if not isinstance(record['real_name'], str):
                    raise ValueError('invalid display name')
                args.real_name = record['real_name']
            args.user = name + ':' + password
        except (ValueError, KeyError, TypeError):
            parser.error('--user-stdin needs a JSON object with string name and password fields')
    if args.real_name is not None and not args.user:
        parser.error('--real-name needs --user, --user-stdin or --interactive-user')
    if args.user is None:
        return
    name, separator, password = args.user.partition(':')
    if not separator or not password or '\0' in password:
        parser.error('the account needs a nonempty password without NUL characters')
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]{0,31}', name) or name.lower() in ('root', 'daemon', 'nobody'):
        parser.error('invalid short account name')
    if args.real_name is not None and (not args.real_name.strip() or any(ord(c) < 32 for c in args.real_name)):
        parser.error('the display name must be nonempty and contain no control characters')


def prompt_account(*, real_name=None, skip_setup=False, auto_login=False):
    """Read credentials from the controlling terminal, outside the build log pipe."""
    if real_name is not None and (not real_name.strip() or any(ord(c) < 32 for c in real_name)):
        raise ValueError('the display name must be nonempty and contain no control characters')
    stack = contextlib.ExitStack()
    try:
        terminal = stack.enter_context(open('/dev/tty', 'w', buffering=1))
        terminal_input = stack.enter_context(open('/dev/tty', 'r'))
    except OSError as error:
        stack.close()
        raise RuntimeError('Account creation needs an interactive terminal') from error
    with stack:
        blue = '\033[94m' if os.environ.get('UNIXNU_LOG_COLOR') == '1' else ''
        reset = '\033[0m' if blue else ''
        terminal.write(f'\n{blue}[INPUT]{reset} Create the macOS administrator\n'
                       'Short account name - login name and /Users directory, for example admin\n'
                       'Display name - shown by macOS, for example Admin\n'
                       'Both identify the same administrator account\n')

        def ask(prompt):
            terminal.write(prompt)
            terminal.flush()
            value = terminal_input.readline()
            if not value:
                raise RuntimeError('Account input was interrupted')
            return value.strip()

        while True:
            name = ask('Short account name [admin]: ') or 'admin'
            if re.fullmatch(r'[a-z][a-z0-9_-]{0,31}', name) and name not in ('root', 'daemon', 'nobody'):
                break
            terminal.write('Use 1-32 lowercase letters, digits, underscores or hyphens; start with a letter\n')
        default = real_name or ('Admin' if name == 'admin' else name)
        while True:
            real_name = ask(f'Display name [{default}]: ') or default
            if not any(ord(c) < 32 for c in real_name):
                break
            terminal.write('The display name cannot contain control characters\n')
        while True:
            password = getpass.getpass('New administrator password (hidden): ', stream=terminal)
            confirmation = getpass.getpass('Confirm password (hidden): ', stream=terminal)
            if password and '\0' not in password and password == confirmation:
                break
            terminal.write('Passwords must be nonempty and match\n')
        if skip_setup:
            terminal.write('Setup Assistant will be skipped\n')
        if auto_login:
            terminal.write('Automatic login will be enabled\n')
    return name, real_name, password
