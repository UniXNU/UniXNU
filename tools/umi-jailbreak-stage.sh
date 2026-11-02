#!/bin/bash
# tools/umi-jailbreak-stage.sh OUTDIR: build the umi jailbreak tree (Procursus rootful bootstrap + Sileo) on the
# Mac, ready for tools/umi-push-staged.py. Downloads (SHA-256 pinned, nothing from this repo):
#   Procursus bootstrap-iphoneos-arm.tar.zst (rootful, 1700 base; 20.6 MB) + .asc,
#   Sileo 2.5.1 rootful deb (GitHub Sileo/Sileo), Procursus libkrw0-tfp0 1.1.1-2 (apt refuses every install
#   while the bootstrap's libkrw0 has no plugin).
# Then: Apple's /usr/bin/ltop and /usr/libexec/dirs_cleaner are kept (bootstrap copies dropped),
# prep_bootstrap.sh is dropped (no shell to run it) and its useful part done here (the dpkg entries
# /usr/libexec/firmware writes), procursus.sources -> suite iphoneos-arm64/1800, dpkg entries for Sileo and
# libkrw0-tfp0, MODES.txt from the tar headers. NOTES.md (umi 0230) has the story.
#   tools/umi-jailbreak-stage.sh OUT
#   tools/umi-push-staged.py OUT/root OUT/modes.txt OUT/push.log
# Afterwards boot once with sweetlsreset=1 so LaunchServices picks up Sileo.app.
set -euo pipefail
[[ $# -eq 1 ]] || { sed -n '2,13p' "$0"; exit 2; }
out=$1
mkdir -p "$out/dl"
out=$(cd "$out" && pwd)
P=https://apt.procurs.us
fetch() { # URL FILE SHA256
	[[ -f $out/dl/$2 ]] || curl -fsSL -o "$out/dl/$2" "$1"
	echo "$3  $out/dl/$2" | shasum -a 256 -c - >/dev/null || { echo "SHA-256 mismatch: $2" >&2; exit 1; }
}
fetch $P/bootstraps/iphoneos-arm64/1700/bootstrap-iphoneos-arm.tar.zst bs.tar.zst \
	8913a49e2b27c433ede53a3f807f7d33d295b867f009134ff04a56dcc79a351b
curl -fsSL -o "$out/dl/bs.tar.zst.asc" $P/bootstraps/iphoneos-arm64/1700/bootstrap-iphoneos-arm.tar.zst.asc
fetch https://github.com/Sileo/Sileo/releases/download/2.5.1/org.coolstar.sileo_2.5.1_iphoneos-arm.deb sileo.deb \
	85f4d93ce78d2a84b776abf91adcbdac41746e751aa3506daaceddabfbf38599
fetch $P/pool/main/iphoneos-arm64/1700/libkrw/libkrw0-tfp0_1.1.1-2_iphoneos-arm.deb krw.deb \
	c2350118f1f29e3cbe30827550c1363776c78a80ffe1004d24c62bdb63269cb0

rm -rf "$out/root" "$out/ctl-sileo" "$out/ctl-krw"
mkdir -p "$out/root"
zstd -dqf "$out/dl/bs.tar.zst" -o "$out/dl/bs.tar"
tar -xpf "$out/dl/bs.tar" -C "$out/root"
python3 -I - "$out/dl/bs.tar" "$out/modes.txt" <<'EOF'
import sys, tarfile
with tarfile.open(sys.argv[1]) as t, open(sys.argv[2], 'w') as f:
    for m in t.getmembers():
        p = m.name[1:] if m.name.startswith('.') else m.name
        if p not in ('', '/'):
            f.write(f'{m.mode:o} {p}\n')
EOF
R=$out/root
rm -f "$R/usr/bin/ltop" "$R/usr/libexec/dirs_cleaner" "$R/prep_bootstrap.sh"
sed -i '' 's|^Suites: iphoneos-arm64/1700$|Suites: iphoneos-arm64/1800|' "$R/private/etc/apt/sources.list.d/procursus.sources"

dpkg-deb -x "$out/dl/sileo.deb" "$R"
dpkg-deb -x "$out/dl/krw.deb" "$R"
dpkg-deb -e "$out/dl/sileo.deb" "$out/ctl-sileo"
dpkg-deb -e "$out/dl/krw.deb" "$out/ctl-krw"
echo '4755 /Applications/Sileo.app/giveMeRoot' >> "$out/modes.txt"
echo '755 /usr/lib/libkrw/libkrw-tfp0.dylib' >> "$out/modes.txt"

D=$R/Library/dpkg
echo 16.7.16 > "$D/info/firmware.ver"
while IFS='|' read -r n v d; do
	printf '\nPackage: %s\nEssential: yes\nStatus: install ok installed\nPriority: required\nSection: System\nInstalled-Size: 0\nArchitecture: iphoneos-arm\nVersion: %s\nDescription: %s\nMaintainer: Jay Freeman (saurik) <saurik@saurik.com>\nTag: role::cydia\n' "$n" "$v" "$d"
done >> "$D/status" <<'EOF'
firmware|16.7.16|almost impressive Apple frameworks
cy+os.ios|16.7.16|virtual operating system dependency
cy+cpu.arm64|0|virtual CPU dependency
cy+model.iphone|10.3|virtual model dependency
cy+kernel.darwin|22.6.0|virtual kernel dependency
cy+lib.corefoundation|1971.0|virtual corefoundation dependency
EOF
for c in "$out/ctl-sileo" "$out/ctl-krw"; do
	(echo; awk '/^Package:/{print; print "Status: install ok installed"; next} NF{print}' "$c/control") >> "$D/status"
done
cp "$out/ctl-sileo/postinst" "$D/info/org.coolstar.sileo.postinst"
cp "$out/ctl-sileo/prerm" "$D/info/org.coolstar.sileo.prerm"
cp "$out/ctl-krw/md5sums" "$D/info/libkrw0-tfp0.md5sums"
(echo /.; dpkg-deb -c "$out/dl/sileo.deb" | awk '{print $NF}' | sed -e 's|^\./|/|' -e 's|/$||' | grep -v '^/*$') \
	> "$D/info/org.coolstar.sileo.list"
(echo /.; dpkg-deb -c "$out/dl/krw.deb" | awk '{print $NF}' | sed -e 's|^\./|/|' -e 's|/$||' | grep -v '^/*$') \
	> "$D/info/libkrw0-tfp0.list"

echo "staged: $R ($(find "$R" | wc -l | tr -d ' ') entries, $(grep -c '^Package:' "$D/status") dpkg packages)"
echo "signature: gpg --verify $out/dl/bs.tar.zst.asc $out/dl/bs.tar.zst (Procursus key C59F3798A305ADD7E7E6C7256430292CF9551B0E)"
echo "push: tools/umi-push-staged.py $R $out/modes.txt $out/push.log"
