#!/usr/bin/env python3
"""Print runtime Metal-library paths from one read-only mounted OS image."""
import os
from pathlib import Path
import sys


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: list-metal-libraries.py MOUNT RUNTIME_PREFIX')
    mount, prefix = Path(sys.argv[1]).resolve(), sys.argv[2].rstrip('/')
    paths = set()

    def failed(error):
        raise error

    for directory, dirs, files in os.walk(mount, followlinks=False, onerror=failed):
        if Path(directory) == mount:
            dirs[:] = [name for name in dirs if name not in ('.Trashes', '.Spotlight-V100', '.fseventsd')]
        for name in files:
            if not name.endswith('.metallib'):
                continue
            relative = (Path(directory) / name).relative_to(mount).as_posix()
            template = 'System/Library/Templates/Data/'
            if not prefix and relative.startswith(template):
                relative = relative[len(template):]
            paths.add(prefix + '/' + relative)
    for path in sorted(paths):
        print(path)


if __name__ == '__main__':
    main()
