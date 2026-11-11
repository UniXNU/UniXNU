# metal2vulkan bridge patches (SweetMetal2)

Applied in file-name order to steelbrain/metal2vulkan @ 720ef1ce (the tree in `xnu-work/work/metal2vulkan`).
0001-0016, 0100-0102 are ios-apollo's series (`userland/metal2/metal2/bridge/patches`, aTechGeekDev/ios-apollo,
same Adreno 650 + Turnip stack); 0100 matches ours byte for byte. Our earlier 0101 (alias every padded writer) is
replaced by apollo's 0008 + 0016 + 0101: padded IOSurface writers alias only where a 16x4 GMEM tile store stays
inside the row pitch and the buffer, otherwise they shadow.

`bridge-alias-writes.diff` is the matching change to the bridge's `NativeMetalObjects.rs`
(`padded_reads = AliasWrites`, `refuse_rebinds = true`).

Build: `xnu-work/work/m2v-bridge` (cargo 1.98, `--target aarch64-apple-ios`), then link SweetMetal2 with
`xcrun -sdk iphoneos clang++ -target arm64-apple-ios16.0` from `m2v-bridge-src` (see NOTES, 2026-11-05).
