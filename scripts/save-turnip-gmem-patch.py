#!/usr/bin/env python3
"""Regenerate patches/mesa/turnip-gmem-mutable-swap.patch from the working Mesa tree.

The patch is the difference between "pinned Mesa + the earlier recorded patches" and the working tree for the files it
touches (the swap of a linear mutable view in GMEM loads and stores, and the render pass telemetry), so it applies last. Edit the Mesa
tree, run this, then run build-adreno-compiler-host.py to prove the tree equals the recorded patches."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MESA = ROOT / '.cache/mesa-work'
MINE = ['src/freedreno/fdl/fd6_view.cc', 'src/freedreno/vulkan/tu_clear_blit.cc', 'src/freedreno/vulkan/tu_cmd_buffer.cc',
        'src/freedreno/vulkan/tu_clear_blit.h', 'src/freedreno/vulkan/tu_knl_darwin.cc', 'src/freedreno/vulkan/tu_cmd_buffer.h',
        'src/freedreno/vulkan/tu_pipeline.cc', 'src/freedreno/vulkan/tu_pipeline.h']
OUT = ROOT / 'patches/mesa/turnip-gmem-mutable-swap.patch'
listed = json.loads((ROOT / 'scripts/data/adreno-compiler-inputs.json').read_text())['patches']
others = listed[:listed.index(str(OUT.relative_to(ROOT)))]


def git(tmp, *args, check=True):
    return subprocess.run(['git', '-c', 'user.email=a@b', '-c', 'user.name=n', *args], cwd=tmp, check=check,
                          capture_output=True, text=True).stdout


tmp = Path(tempfile.mkdtemp(dir=ROOT / '.cache'))
try:
    git(tmp, 'init', '-q')
    for f in MINE:
        shown = subprocess.run(['git', 'show', 'HEAD:' + f], cwd=MESA, capture_output=True)
        if shown.returncode:   # a file an earlier recorded patch creates
            continue
        (tmp / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp / f).write_bytes(shown.stdout)
    git(tmp, 'add', '-A')
    git(tmp, 'commit', '-q', '-m', 'base')
    for patch in others:
        for f in MINE:
            git(tmp, 'apply', '--include=' + f, str(ROOT / patch), check=False)
    git(tmp, 'add', '-A')
    git(tmp, 'commit', '-q', '-m', 'others', '--allow-empty')
    for f in MINE:
        shutil.copy(MESA / f, tmp / f)
    OUT.write_text(git(tmp, 'diff', '--binary'))
finally:
    shutil.rmtree(tmp)
print('wrote', OUT.relative_to(ROOT), len(OUT.read_text().splitlines()), 'lines')
