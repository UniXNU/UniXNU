#!/usr/bin/env python3
"""Patch the assembled tree for the reproducible bring-up build.

Two independent gaps, both in sources the public repositories ship:

  * NativeUfs keeps an optional read-timing instrumentation that needs timerTicks()
    and a per-driver counter, neither of which exists in this configuration;
  * bsd_init references native_legacy_display_probe() unconditionally under
    DEVELOPMENT || DEBUG, and that probe only exists in the legacy display driver.

The timing helpers become no-ops, and the display probe gets a weak fallback compiled
into an archive the link already force-loads, so the real definition wins whenever the
legacy display archive is part of the link.
"""
import sys
from pathlib import Path

TIMING = (
    '/* Bring-up build: the timing instrumentation helpers are not available here. */',
    'static uint64_t native_ufs_read_ticks;',
    'static inline uint64_t timerTicks(void) { return 0; }',
)

STUB = (
    '/* Bring-up: weak fallback for the optional legacy display probe. */\n'
    'extern "C" void native_legacy_display_probe(void) __attribute__((weak));\n'
    'extern "C" void native_legacy_display_probe(void) {}\n'
)

UFS_PATHS = (
    Path('device/drivers/NativeUfs/NativeUfs.cpp'),
    Path('out/sheng/tree/drivers/NativeUfs/NativeUfs.cpp'),
)

AES_DIRS = (
    Path('device/drivers/NativeAES'),
    Path('out/sheng/tree/drivers/NativeAES'),
)


def patch_timing(path):
    if not path.is_file():
        return f'skipped {path}'
    text = path.read_text()
    if 'timerTicks' not in text:
        return f'{path}: no timing instrumentation'
    if TIMING[1] in text:
        return f'{path}: already patched'
    lines = text.splitlines(keepends=True)
    last_include = max((i for i, line in enumerate(lines) if line.startswith('#include')), default=None)
    if last_include is None:
        return f'{path}: no include block'
    block = ''.join(line + '\n' for line in TIMING)
    lines.insert(last_include + 1, '\n' + block)
    path.write_text(''.join(lines))
    return f'{path}: inserted the timing helpers'


def patch_stub(directory):
    if not directory.is_dir():
        return f'skipped {directory}'
    sources = sorted(directory.glob('*.cpp')) or sorted(directory.glob('*.c'))
    if not sources:
        return f'{directory}: no sources'
    source = sources[0]
    body = source.read_text()
    if 'native_legacy_display_probe' in body:
        return f'{source}: already carries the stub'
    source.write_text(body + '\n' + STUB)
    return f'{source}: appended the weak display probe'


for candidate in UFS_PATHS:
    print(patch_timing(candidate))
for candidate in AES_DIRS:
    print(patch_stub(candidate))
sys.exit(0)
