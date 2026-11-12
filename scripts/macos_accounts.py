"""Local accounts and Setup preferences for a fresh macOS Data volume."""
import hashlib
import os
import plistlib
import subprocess
import uuid

DSLOCAL = 'private/var/db/dslocal/nodes/Default'
SETUP_SKIP = 'Library/Managed Preferences/com.apple.SetupAssistant.managed.plist'
LOGINWINDOW_PREFS = 'Library/Preferences/com.apple.loginwindow.plist'
KCPASSWORD = 'private/etc/kcpassword'
KEYBOARD_TYPE = 'Library/Preferences/com.apple.keyboardtype.plist'
USER_TEMPLATE = 'Library/User Template'
KCPASSWORD_KEY = bytes.fromhex('7d895223d2bcddeaa3b91f')
SETUP_SKIP_ITEMS = ['Accessibility', 'AdditionalPrivacySettings', 'Appearance', 'AppleID', 'AppStore', 'Biometric', 'Diagnostics',
                    'DisplayTone', 'EnableLockdownMode', 'FileVault', 'iCloudDiagnostics', 'iCloudStorage', 'Intelligence', 'Location',
                    'OSShowcase', 'Privacy', 'Restore', 'Safety', 'ScreenTime', 'Siri', 'SoftwareUpdate', 'TermsOfAddress', 'TextSize',
                    'TOS', 'TouchIDPrompt', 'UnlockWithWatch', 'Wallpaper', 'Welcome']

def write_root(path, data, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    os.chown(path, 0, 0)
    path.chmod(mode)


def add_user(dslocal, name, password, uid=501):
    """A local administrator as System Settings writes one: the user record and its admin and staff memberships."""
    salt, iterations = os.urandom(32), 50000
    entropy = hashlib.pbkdf2_hmac('sha512', password.encode(), salt, iterations, 128)
    shadow = plistlib.dumps({'SALTED-SHA512-PBKDF2': {'entropy': entropy, 'iterations': iterations, 'salt': salt}},
                            fmt=plistlib.FMT_BINARY)
    guid = str(uuid.uuid4()).upper()
    write_root(dslocal / 'users' / (name + '.plist'), plistlib.dumps({
        'name': [name], 'realname': [name], 'uid': [str(uid)], 'gid': ['20'], 'home': ['/Users/' + name], 'shell': ['/bin/zsh'],
        'generateduid': [guid], 'passwd': ['********'], 'authentication_authority': [';ShadowHash;HASHLIST:<SALTED-SHA512-PBKDF2>'],
        'ShadowHashData': [shadow], '_writers_passwd': [name], '_writers_realname': [name], '_writers_hint': [name]},
        fmt=plistlib.FMT_BINARY), 0o600)
    for group in ('admin', 'staff'):
        path = dslocal / 'groups' / (group + '.plist')
        record = plistlib.loads(path.read_bytes())
        record['users'] = [u for u in record.get('users', []) if u != name] + [name]
        record['groupmembers'] = [g for g in record.get('groupmembers', []) if g != guid] + [guid]
        write_root(path, plistlib.dumps(record, fmt=plistlib.FMT_BINARY), 0o600)


def add_home(template, mount, name, uid=501, gid=20):
    """The user's home as createhomedir makes it (the template's unlocalized part, then its English one), owned by the user, with
    .skipbuddy: Setup Assistant's MiniBuddy does not run for it."""
    home = mount / 'Users' / name
    home.mkdir(parents=True)
    for part in ('Non_localized', 'English.lproj'):
        source = template / USER_TEMPLATE / part
        if source.is_dir():
            subprocess.run(['ditto', '--rsrc', '--extattr', source, home], check=True)
    (home / '.skipbuddy').touch()
    subprocess.run(['chown', '-R', f'{uid}:{gid}', home], check=True)
    home.chmod(0o750)
    # A home's own folders are the user's alone, as on an installed system; Public and its Drop Box follow the template's list.
    for private in ('Desktop', 'Documents', 'Downloads', 'Library', 'Movies', 'Music', 'Pictures'):
        if (home / private).is_dir():
            (home / private).chmod(0o700)
    # The template's own permission list (__permissions.plist): its CHMOD entries.
    permissions = template / USER_TEMPLATE / '__permissions.plist'
    for entry in plistlib.loads(permissions.read_bytes()) if permissions.is_file() else []:
        for path in entry.get('Paths', []) if entry.get('Command') == 'CHMOD' else []:
            target = home / path.lstrip('/')
            if target.exists():
                target.chmod(int(entry['Argument'], 8))


def add_keyboard_types(mount, entries):
    types = {}
    for entry in entries:
        key, _, value = entry.partition('=')
        if not value.isdigit() or len(key.split('-')) != 3 or not all(part.isdigit() for part in key.split('-')):
            raise SystemExit(f'--keyboard-type {entry}: expected PRODUCT-VENDOR-COUNTRY=TYPE in decimal')
        types[key] = int(value)
    write_root(mount / KEYBOARD_TYPE, plistlib.dumps({'keyboardtype': types}, fmt=plistlib.FMT_XML), 0o644)


def kcpassword(password):
    """/etc/kcpassword as loginwindow reads it: the password and its terminator, padded to 12-byte blocks, XORed with the cyclic key."""
    data = password.encode() + b'\0'
    data += bytes(-len(data) % 12)
    return bytes(b ^ KCPASSWORD_KEY[i % len(KCPASSWORD_KEY)] for i, b in enumerate(data))


def add_auto_login(mount, name, password):
    path = mount / LOGINWINDOW_PREFS
    prefs = plistlib.loads(path.read_bytes()) if path.is_file() else {}
    prefs['autoLoginUser'] = name
    write_root(path, plistlib.dumps(prefs, fmt=plistlib.FMT_BINARY), 0o644)
    write_root(mount / KCPASSWORD, kcpassword(password), 0o600)
