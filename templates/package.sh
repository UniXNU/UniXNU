#!/usr/bin/env bash
# Device packaging script, identical in every device repository. Do not edit it: a board changes board.toml
# ([package] and the sections it names), never this file. Steps (run by "unixnu release"): deps, preflight,
# patches, build, pack, verify. Documentation: docs/porting/packaging.md in the UniXNU repository.
# usage: scripts/package.sh [--os 17|26|27|PROFILE] [--no-deps] [--check] [any other unixnu option]
set -euo pipefail
DEVICE=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
UNIXNU=$(python3 - "$DEVICE/board.toml" <<'PY'
import sys, tomllib
package = tomllib.load(open(sys.argv[1], 'rb')).get('package', {})
if 'unixnu' not in package:
    sys.exit('board.toml needs [package] unixnu = "<path of the UniXNU checkout, relative to this repository>"')
print(package['unixnu'])
PY
)
case "$UNIXNU" in /*) ROOT=$UNIXNU ;; *) ROOT=$(cd "$DEVICE/$UNIXNU" && pwd) ;; esac
exec python3 "$ROOT/unixnu" release -D "$DEVICE" "$@"
