#!/usr/bin/env python3
"""Summarize a render server's shader-priming capture from its cache directory."""
import argparse
import json
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cache', type=Path, help='directory containing prime.log and the priming checkpoints')
    args = parser.parse_args()
    log = args.cache / 'prime.log'
    lines = log.read_text(errors='replace').splitlines()
    start = max((i for i, line in enumerate(lines) if line.startswith('list ') and ' build=' in line), default=0)
    lines = lines[start:]
    build = lines[0].rpartition(' build=')[2] if lines else ''
    summary = next((line for line in reversed(lines) if line.startswith('pass ')), '')
    counts = {key: int(value) for key, value in re.findall(r'(?:^| )([a-z-]+)=(\d+)(?= |$)', summary)}
    state = {0: 'in-progress', 1: 'complete', 2: 'incomplete'}.get(counts.get('complete', 0), 'unknown')
    if summary and 'complete' not in counts:
        state = 'unclassified'
    refused = []
    for line in lines:
        if line.startswith('/') and (' library refused:' in line or re.search(r' (?:refused|skipped)=[1-9]\d*', line)):
            refused.append(line)
    checkpoints = {}
    for name in ('prime-done', 'prime-fn2', 'prime-refused2', 'prime-bad', 'prime-current'):
        path = args.cache / name
        if path.is_file():
            checkpoint_build = build
            if name == 'prime-refused2' and counts.get('inputs', 0) >= 3:
                checkpoint_build += '-inputs' + str(counts['inputs'])
            checkpoints[name] = sum(line.endswith('\t' + checkpoint_build) for line in path.read_text(errors='replace').splitlines())
    print(json.dumps({'state': state, 'coverage': 'default kernel and vertex pipeline variants',
                      'build': build, 'counts': counts, 'checkpoints': checkpoints,
                      'refused_libraries': refused}, indent=2))


if __name__ == '__main__':
    main()
