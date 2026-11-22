#!/usr/bin/env python3
"""Check the bridge's root runtime imports before compiling GPU dependencies.

This source check catches removed public exports. Rust type checking is still
required for method signatures, lifetimes, feature gates and ABI compatibility.
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source_text(path):
    # Consumer imports contain no macros. Strip comments before scanning uses.
    text = re.sub(r'/\*.*?\*/', '', path.read_text(), flags=re.S)
    return re.sub(r'//[^\n]*', '', text)


def public_roots(path):
    text = source_text(path)
    names = set(re.findall(r'^pub\s+(?:unsafe\s+)?(?:struct|enum|trait|type|const|mod|fn)\s+(\w+)', text, re.M))
    for statement in re.findall(r'^pub\s+use\s+([^;]+);', text, re.M):
        if '{' in statement:
            items = statement[statement.index('{') + 1:statement.rindex('}')]
            for item in items.split(','):
                item = item.strip()
                if item:
                    names.add(item.split(' as ')[-1].split('::')[-1].strip())
        else:
            names.add(statement.split(' as ')[-1].split('::')[-1].strip())
    return names


def required_roots(bridge):
    required = {}
    for path in sorted(bridge.glob('*.rs')):
        text = source_text(path)
        for group in re.findall(r'\buse\s+metal2vulkan_runtime::\{([^}]+)\}', text, re.S):
            for item in group.split(','):
                name = item.strip().split(' as ')[0].split('::')[0]
                if name:
                    required.setdefault(name, set()).add(path.name)
        for name in re.findall(r'\bmetal2vulkan_runtime::(\w+)', text):
            required.setdefault(name, set()).add(path.name)
    return required


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / '.cache/gpu-reference/metal2vulkan')
    parser.add_argument('--bridge', type=Path, default=ROOT / 'drivers/AdrenoMetal/bridge')
    args = parser.parse_args()
    exports = public_roots(args.source / 'crates/metal2vulkan-runtime/src/lib.rs')
    required = required_roots(args.bridge)
    missing = sorted(set(required) - exports)
    if missing:
        print(f'FAIL: runtime does not export {len(missing)} bridge dependencies:')
        for name in missing:
            print(f'  {name}: {", ".join(sorted(required[name]))}')
        print('Port the bridge to this runtime before building or packaging the GPU plugin.')
        return 1
    print(f'PASS: {len(required)} runtime root imports are exported; Rust type checking remains required')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
