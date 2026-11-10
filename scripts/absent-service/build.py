#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Build the stand-in for system daemons that cannot run on a board (absentd.c): OUT/bin/unixnu-absentd, signed ad hoc."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
parser.add_argument('target', choices=('macos27',))
args = parser.parse_args()
out = args.output.resolve()
(out / 'bin').mkdir(parents=True, exist_ok=True)
binary = out / 'bin/unixnu-absentd'
sdk = subprocess.check_output(['xcrun', '--sdk', 'macosx', '--show-sdk-path'], text=True).strip()
subprocess.run(['xcrun', 'clang', '-target', 'arm64e-apple-macos27.0', '-isysroot', sdk, '-Os', '-Wall', '-Wextra', '-Werror',
                '-fblocks', '-framework', 'CoreFoundation', '-o', binary, root / 'absentd.c'], check=True)
subprocess.run(['codesign', '--force', '--sign', '-', '--pagesize', '4096', '--identifier', 'org.unixnu.absentd', binary], check=True)
subprocess.run(['codesign', '--verify', '--strict', binary], check=True)
detail = subprocess.run(['codesign', '--display', '--verbose=4', binary], check=True, capture_output=True, text=True).stderr
match = re.search(r'^CDHash=([0-9a-f]{40})$', detail, re.M)
if not match:
    raise SystemExit('signed stand-in has no CDHash')
(out / 'report.json').write_text(json.dumps({'built': True, 'target': args.target, 'cdhash': match[1],
    'files': {'bin/unixnu-absentd': hashlib.sha256(binary.read_bytes()).hexdigest()}}, indent=2) + '\n')
