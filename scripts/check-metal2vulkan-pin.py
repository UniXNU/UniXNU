#!/usr/bin/env python3
"""Check the translator source the native Metal bridge builds from against upstream, by git alone.

1. The pin (scripts/data/gpu-metal-vulkan-inputs.json) is a commit of the upstream branch it names (master when it names none); with
   --latest, that branch's tip (fetched now).
2. The checkout (.cache/gpu-reference/metal2vulkan) is at the pin.
3. The recorded patches (the list build-adreno-metal-bridge.py applies) apply in order to the pin's own tree, in a scratch index, with no
   three-way merge and no fuzz.
4. The checkout's tree is the pin's tree or the pin's tree plus every patch, nothing else: every byte of every other file is upstream's.
5. The pinned files' SHA-256 are the pin's.
Prints the files the patches change, with their lines added and removed, and PASS; else FAIL with the first difference."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=ROOT / '.cache/gpu-reference/metal2vulkan')
parser.add_argument('--latest', action='store_true', help="also require the pin to be its upstream branch's tip, fetched now")
args = parser.parse_args()
inputs = json.loads((ROOT / 'scripts/data/gpu-metal-vulkan-inputs.json').read_text())['translator']
pin, branch, source = inputs['commit'], inputs.get('branch', 'master'), args.source


def git(*argv, env=None, check=True):
    result = subprocess.run(['git', '-C', str(source)] + list(argv), env=env, capture_output=True, text=True)
    if check and result.returncode:
        fail('git %s: %s' % (' '.join(argv), result.stderr.strip()))
    return result


def fail(why):
    print('FAIL: ' + why)
    sys.exit(1)


# The patch list exactly as the bridge build reads it.
build = (ROOT / 'scripts/build-adreno-metal-bridge.py').read_text()
listed = build[build.index('PATCHES = ['):build.index(']]', build.index('PATCHES = ['))]
names = re.findall(r"'(\d{4}-[^']+\.patch)'", listed)
directory = ROOT / 'drivers/AdrenoMetal/bridge/patches'
on_disk = sorted(p.name for p in directory.glob('*.patch'))
if sorted(names) != on_disk:
    fail('the build lists %s, the directory holds %s' % (names, on_disk))
patches = [directory / name for name in names]

# Runtime checkouts fetched by hash need not have an origin remote.
# Verify against the repository in the selected pin record.
git('fetch', '-q', inputs['repository'], '+refs/heads/%s:refs/remotes/upstream/%s' % (branch, branch))
tip = git('rev-parse', 'upstream/' + branch).stdout.strip()
if git('merge-base', '--is-ancestor', pin, 'upstream/' + branch, check=False).returncode:
    fail('pin %s is no commit of upstream %s' % (pin, branch))
behind = int(git('rev-list', '--count', '%s..upstream/%s' % (pin, branch)).stdout)
if args.latest and pin != tip:
    fail('pin %s is %d commits behind upstream %s %s' % (pin[:12], behind, branch, tip[:12]))
head = git('rev-parse', 'HEAD').stdout.strip()
if head != pin:
    fail('checkout at %s, pin %s' % (head, pin))


def tree(*steps):
    index = ROOT / 'build/check-metal2vulkan-index'
    index.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    git('read-tree', pin, env=env)
    for step in steps:
        git(*step, env=env)
    out = git('write-tree', env=env).stdout.strip()
    index.unlink()
    return out


pinned = git('rev-parse', pin + '^{tree}').stdout.strip()
patched = tree(*[['apply', '--cached', str(p)] for p in patches])
current = tree(['add', '-A'])
if current not in (pinned, patched):
    changed = git('diff', '--stat', patched, current).stdout
    fail('the checkout is neither the pin nor the pin plus the patches; against the patched tree:\n' + changed)
for name, digest in inputs['files'].items():
    blob = subprocess.run(['git', '-C', str(source), 'show', '%s:%s' % (pin, name)], capture_output=True)
    if blob.returncode or hashlib.sha256(blob.stdout).hexdigest() != digest:
        fail('pinned file %s differs from the pin record' % name)
print('upstream %s %s, pin %s (%d commits behind), checkout %s' % (branch, tip[:12], pin[:12], behind,
      'patched' if current == patched else 'unpatched'))
for line in git('diff', '--numstat', pinned, patched).stdout.splitlines():
    added, removed, path = line.split('\t')
    print('  +%-5s -%-5s %s' % (added, removed, path))
print('PASS: %d patches over upstream %s; every other file is upstream\'s byte for byte' % (len(patches), pin[:12]))
