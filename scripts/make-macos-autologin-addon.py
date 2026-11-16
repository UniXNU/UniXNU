#!/usr/bin/env python3
"""Add administrator-selected automatic login to a macOS runtime addon."""
import argparse
import importlib.util
import os
from pathlib import Path
import plistlib
import re
import sys


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


INSTALLER = '''#!/bin/sh
set -eu
/bin/mkdir -p /Users/Shared/unixnu-test
exec >>/Users/Shared/unixnu-test/daemon.log 2>&1
/bin/date -u
/usr/sbin/sysctl -n kern.bootsessionuuid
base='/Library/Application Support/UniXNU/AutoLogin'
user=$(/bin/cat "$base/user")
/usr/bin/id "$user" >/dev/null
/usr/bin/pmset -a displaysleep 0 sleep 0 || /usr/bin/logger -t UniXNUAutoLogin 'pmset failed'
/usr/bin/sudo -H -u "$user" /usr/bin/defaults -currentHost write com.apple.screensaver idleTime -int 0 || /usr/bin/logger -t UniXNUAutoLogin 'Screensaver preference failed'
changed=0
if ! /usr/bin/cmp -s "$base/kcpassword" /private/etc/kcpassword; then
    /usr/bin/install -o root -g wheel -m 600 "$base/kcpassword" /private/etc/kcpassword
    changed=1
fi
current=$(/usr/bin/defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser 2>/dev/null || :)
if [ "$current" != "$user" ]; then
    /usr/bin/defaults write /Library/Preferences/com.apple.loginwindow autoLoginUser -string "$user"
    changed=1
fi
locked=$(/usr/bin/defaults read /Library/Preferences/com.apple.loginwindow autoLoginUserScreenLocked 2>/dev/null || :)
if [ "$locked" != 0 ]; then
    /usr/bin/defaults write /Library/Preferences/com.apple.loginwindow autoLoginUserScreenLocked -bool false
    changed=1
fi
/usr/bin/logger -t UniXNUAutoLogin "Automatic login configured for $user"
/bin/echo "Automatic login configured for $user; changed=$changed"
/usr/bin/pmset -g custom || :
/usr/sbin/sysadminctl -autologin status 2>&1 || :
/usr/bin/defaults read /Library/Preferences/com.apple.loginwindow 2>&1 || :
/usr/bin/defaults read /Library/Preferences/com.apple.screensaver 2>&1 || :
if [ "$changed" = 1 ]; then
    /usr/bin/killall -TERM loginwindow 2>/dev/null || :
fi
/bin/sleep 60
/bin/echo "Login state boot=$(/usr/sbin/sysctl -n kern.bootsessionuuid)"
/usr/bin/stat -f '%Su %u' /dev/console
/bin/ps -axo pid,ppid,user,etime,comm | /usr/bin/awk 'NR == 1 || /loginwindow|WindowServer|Finder|Dock|Setup Assistant|ScreenSaver|caffeinate/'
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--user', required=True)
    parser.add_argument('--password-stdin', action='store_true', required=True,
                        help='read the existing account password from standard input')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,30}', args.user):
        parser.error('use a local account short name')
    if args.output.exists() or args.input.resolve() == args.output.resolve():
        parser.error('choose a new output file')
    password = sys.stdin.read().rstrip('\r\n')
    if not password or '\0' in password:
        parser.error('require a nonempty account password without NUL bytes')
    key = bytes.fromhex('7d895223d2bcddeaa3b91f')
    encoded = password.encode() + b'\0'
    encoded += bytes(-len(encoded) % 12)
    encoded = bytes(value ^ key[index % len(key)] for index, value in enumerate(encoded))
    codec = module('addon', Path(__file__).with_name('addon-add-dir.py'))
    files = codec.read(args.input)
    prefix = 'Library/Application Support/UniXNU/AutoLogin/'
    job = dict(Label='org.unixnu.autologin', RunAtLoad=True,
               ProgramArguments=['/bin/sh', '/' + prefix + 'install.sh'],
               StandardOutPath='/private/var/log/unixnu-autologin.log',
               StandardErrorPath='/private/var/log/unixnu-autologin.log')
    awake = dict(Label='org.unixnu.desktop-awake', RunAtLoad=True, KeepAlive=True,
                 ProgramArguments=['/usr/bin/caffeinate', '-d', '-i', '-s'])
    additions = [(prefix + 'user', 0o600, (args.user + '\n').encode()),
                 (prefix + 'kcpassword', 0o600, encoded),
                 (prefix + 'install.sh', 0o700, INSTALLER.encode()),
                 ('Library/LaunchDaemons/org.unixnu.autologin.plist', 0o644, plistlib.dumps(job)),
                 ('Library/LaunchDaemons/org.unixnu.desktop-awake.plist', 0o644, plistlib.dumps(awake))]
    names = {name for name, _, _ in additions}
    files = [entry for entry in files if entry[0] not in names] + additions
    os.umask(0o077)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    codec.write(args.output, files)
    print(f'{args.output}: automatic login for {args.user}')


if __name__ == '__main__':
    main()
