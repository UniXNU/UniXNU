#!/usr/bin/env python3
"""Prepare the sheng device tree for the reproducible kernel build.

Two modes:

  bootstrap (default)  only the archive builders whose inputs the pinned sources
                       provide, and a defconfig with the matching gates. This pass has
                       to link first, because its kernel is what the prelink candidates
                       are made from.
  --full               additionally the driver archives that audit the original kexts
                       against build/native-prelink candidates. Run after .ci/make_candidates.py.

The recipe follows the reference port (Allenwdk/UniXNU-uke).
"""
import shutil
import sys
from pathlib import Path

DEVICE = Path('device')
VENDOR = Path('.ci/scripts')

OVERLAY = (
    'build-arm-driver.py',
    'prepare-storage-headers.py',
    'build-ufs-original-bindings.py',
)

BASE_ARCHIVES = [
    'build-corecrypto-14.py',
    'build-corecrypto-14.py --namespace',
    'build-arm-driver.py ArmDTPlatform',
    'build-arm-driver.py ArmCpu',
    'build-arm-driver.py NativeAES',
    'build-native-aes-bindings.py',
    'prepare-storage-headers.py',
    'build-arm-driver.py NativeRamBlock',
]

DRIVER_ARCHIVES = [
    'build-arm-driver.py NativeUfs --unverified',
    'build-ufs-original-bindings.py',
    'build-sheng-platform-power.py',
]

TAIL_ARCHIVES = [
    'build-libpthread-kernel.py',
]

FEED = '''[[source]]
name = "IOStorageFamily"
kind = "refer"
git = "https://github.com/apple-oss-distributions/IOStorageFamily.git"
ref = "main"
commit = "e45fbe30a7879e0b16e26dddb78538f1b00e0bff"

'''


def main(argv):
    full = '--full' in argv

    for name in OVERLAY:
        source = VENDOR / name
        if not source.is_file():
            print(f'missing vendored script {source}')
            return 1
        shutil.copyfile(source, DEVICE / 'scripts' / name)

    entries = BASE_ARCHIVES + (DRIVER_ARCHIVES if full else []) + TAIL_ARCHIVES
    board = DEVICE / 'board.toml'
    text = board.read_text()
    start = text.index('archives = [')
    end = text.index(']', start) + 1
    block = 'archives = [\n' + ''.join(f'  "{entry}",\n' for entry in entries) + ']'
    board.write_text(text[:start] + block + text[end:])
    print(f'archives: {len(entries)} entries ({"full" if full else "bootstrap"})')

    feeds = DEVICE / 'feeds.toml'
    if not feeds.is_file():
        feeds.write_text(FEED)
        print('created device feeds.toml with the IOStorageFamily feed')
    elif 'IOStorageFamily' not in feeds.read_text():
        feeds.write_text(FEED + feeds.read_text())
        print('added the IOStorageFamily feed')

    name = 'sheng-drivers_defconfig' if full else 'sheng-full_defconfig'
    target = DEVICE / 'configs' / name
    shutil.copyfile(Path('.ci') / name, target)
    print(f'wrote {target}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
