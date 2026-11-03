#!/usr/bin/env python3
"""Build the selected Qualcomm baseband component with the target XNU records."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.call([sys.executable, str(ROOT / 'drivers/QcomBaseband/scripts/build.py'), '--tree', str(ROOT), *sys.argv[1:]]))
