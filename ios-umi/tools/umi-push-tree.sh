#!/bin/bash
# Push a local tree onto the phone (umi-files.py): mkdir dirs, rm + put files (mode kept), symlinks,
# then GET each file back and cmp. Usage: tools/umi-push-tree.sh LOCAL-ROOT REMOTE-PATH...
# (REMOTE-PATH is relative to LOCAL-ROOT, e.g. Applications/Sileo.app). Run tools/umi-usbnet.sh first.
set -uo pipefail
F=$(cd "$(dirname "$0")" && pwd)/umi-files.py
root=$1; shift
tmp=$(mktemp -d "${TMPDIR:-/tmp}/sileo-rb.XXXX")
fail=0
for top in "$@"; do
  cd "$root"
  while IFS= read -r p; do
    r=/${p#./}
    if [[ -L $p ]]; then
      python3 $F rm "$r" >/dev/null 2>&1
      python3 $F link "$(readlink "$p")" "$r" >/dev/null || { echo "LINK FAIL $r"; fail=1; }
    elif [[ -d $p ]]; then
      python3 $F mkdir "$r" 755 >/dev/null 2>&1 || true
    else
      python3 $F rm "$r" >/dev/null 2>&1
      python3 $F put "$p" "$r" >/dev/null || { echo "PUT FAIL $r"; fail=1; continue; }
      python3 $F get "$r" "$tmp/rb" >/dev/null && cmp -s "$p" "$tmp/rb" || { echo "VERIFY FAIL $r"; fail=1; }
    fi
  done < <(find "./$top" | sort)
done
rm -rf "$tmp"
echo "done fail=$fail"
exit $fail
