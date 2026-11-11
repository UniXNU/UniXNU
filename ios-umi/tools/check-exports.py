#!/usr/bin/env python3
"""Reproduce xnu's check_all_exports / symbolset check offline.

  check-exports.py XNU_SRC ALLSYMBOLS [PLATFORM]

Every entry of <Set>.exports, <Set>.arm64.exports and <Set>.arm64.<PLATFORM>.exports
must name a symbol present in ALLSYMBOLS (`nm -gj` of the linked kernel, from the
build tree). Entries are "sym" or "exported:sym"; a trailing '*' is a prefix match.
Prints the entries kextsymboltool would reject, per file.
"""
import os, sys

SETS = ['BSDKernel', 'IOKit', 'Libkern', 'Mach', 'MACFramework', 'Unsupported', 'Private']


def main():
    src, allsyms = sys.argv[1], sys.argv[2]
    platform = sys.argv[3] if len(sys.argv) > 3 else 'MacOSX'
    have = set(l.strip() for l in open(allsyms) if l.strip())
    missing_total = 0
    for s in SETS:
        for name in (f'{s}.exports', f'{s}.arm64.exports', f'{s}.arm64.{platform}.exports'):
            path = os.path.join(src, 'config', name)
            if not os.path.exists(path):
                continue
            for line in open(path):
                e = line.split('#')[0].strip()
                if not e:
                    continue
                target = e.split(':', 1)[1].strip() if ':' in e else e
                ok = any(h.startswith(target[:-1]) for h in have) if target.endswith('*') else target in have
                if not ok:
                    print(f'{name}: {e}')
                    missing_total += 1
    print(f'{missing_total} missing', file=sys.stderr)
    return 1 if missing_total else 0


if __name__ == '__main__':
    sys.exit(main())
