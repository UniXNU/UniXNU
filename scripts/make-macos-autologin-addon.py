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
if [ -s "$base/authorized-key" ]; then
    uid=$(/usr/bin/id -u "$user")
    group=$(/usr/bin/id -gn "$user")
    home=$(/usr/bin/dscl . -read "/Users/$user" NFSHomeDirectory | /usr/bin/cut -d ' ' -f 2-)
    /usr/bin/install -d -o "$user" -g "$group" -m 700 "$home/.ssh"
    /usr/bin/touch "$home/.ssh/authorized_keys"
    key=$(/bin/cat "$base/authorized-key")
    /usr/bin/grep -Fqx "$key" "$home/.ssh/authorized_keys" || /bin/echo "$key" >> "$home/.ssh/authorized_keys"
    /usr/sbin/chown "$user:$group" "$home/.ssh/authorized_keys"
    /bin/chmod 600 "$home/.ssh/authorized_keys"
    /bin/launchctl enable system/com.openssh.sshd
    /bin/launchctl bootstrap system /System/Library/LaunchDaemons/ssh.plist 2>/dev/null || :
    /bin/echo "Remote login configured for $user (uid=$uid)"
fi
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
/usr/bin/pmset -g batt || :
/sbin/ifconfig || :
/usr/sbin/sysadminctl -autologin status 2>&1 || :
/usr/bin/defaults read /Library/Preferences/com.apple.loginwindow 2>&1 || :
/usr/bin/defaults read /Library/Preferences/com.apple.screensaver 2>&1 || :
if [ "$changed" = 1 ]; then
    /usr/bin/killall -TERM loginwindow 2>/dev/null || :
fi
/bin/sleep 60
/bin/echo "Login state boot=$(/usr/sbin/sysctl -n kern.bootsessionuuid)"
/usr/bin/stat -f '%Su %u' /dev/console
/bin/ps -axo pid,ppid,user,etime,comm | /usr/bin/awk 'NR == 1 || /loginwindow|WindowServer|Finder|Dock|System Settings|iconservices|Setup Assistant|ScreenSaver|caffeinate/'
'''

GRAPHICS_LOG = '''#!/bin/sh
set -eu
directory=/Users/Shared/unixnu-test
/bin/mkdir -p "$directory"
exec >"$directory/graphics-events.log" 2>&1
boot=$(/usr/sbin/sysctl -n kern.bootsessionuuid)
/bin/echo "graphics capture boot=$boot"
/bin/echo "graphics capture boot=$boot" >"$directory/graphics-state.log"
/usr/bin/log stream --style compact --level info --timeout 120s --predicate '(process == "WindowServer" OR process == "System Settings" OR process == "loginwindow" OR process BEGINSWITH "Wallpaper" OR process CONTAINS[c] "iconservices" OR subsystem CONTAINS[c] "CoreImage" OR subsystem CONTAINS[c] "Metal") AND NOT eventMessage BEGINSWITH "NativeAdrenoMetal table:" AND NOT subsystem BEGINSWITH "com.apple.network" AND NOT subsystem BEGINSWITH "com.apple.CFNetwork" AND NOT subsystem == "com.apple.wallpaper"' | /usr/bin/head -c 1900000
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--user', required=True)
    parser.add_argument('--capture-graphics', action='store_true', help='capture 120 seconds of fresh graphics logs during boot')
    parser.add_argument('--ssh-public-key', type=Path, help='enable Remote Login for this existing account with the supplied public key')
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
    capture = dict(Label='org.unixnu.graphics-log', RunAtLoad=True,
                   Disabled=not args.capture_graphics,
                   ProgramArguments=['/bin/sh', '/' + prefix + 'capture-graphics.sh'])
    additions = [(prefix + 'user', 0o600, (args.user + '\n').encode()),
                 (prefix + 'kcpassword', 0o600, encoded),
                 (prefix + 'install.sh', 0o700, INSTALLER.encode()),
                 (prefix + 'capture-graphics.sh', 0o700, GRAPHICS_LOG.encode()),
                 ('Library/LaunchDaemons/org.unixnu.autologin.plist', 0o644, plistlib.dumps(job)),
                 ('Library/LaunchDaemons/org.unixnu.graphics-log.plist', 0o644, plistlib.dumps(capture)),
                 ('Library/LaunchDaemons/org.unixnu.desktop-awake.plist', 0o644, plistlib.dumps(awake))]
    if args.ssh_public_key:
        key = args.ssh_public_key.read_text().strip().split()
        if len(key) < 2 or key[0] != 'ssh-ed25519' or not re.fullmatch(r'[A-Za-z0-9+/=]+', key[1]):
            parser.error('require an OpenSSH Ed25519 public key')
        additions.append((prefix + 'authorized-key', 0o600, (' '.join(key[:2]) + '\n').encode()))
    names = {name for name, _, _ in additions}
    files = [entry for entry in files if entry[0] not in names] + additions
    os.umask(0o077)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    codec.write(args.output, files)
    print(f'{args.output}: automatic login for {args.user}')


if __name__ == '__main__':
    main()
