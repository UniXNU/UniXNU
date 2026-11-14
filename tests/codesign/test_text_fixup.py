#!/usr/bin/env python3
"""Run the assembled XNU text-fixup and signature functions in a host fixture.

Usage: python3 tests/codesign/test_text_fixup.py --source TREE/.cache/xnu-work/bsd/kern/ubc_subr.c
The fixture replaces VM I/O and hash storage, not the functions under test.
"""
import argparse
import ctypes
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


def function(source: str, name: str) -> str:
    match = re.search(r"\n(?:static )?[\w *]+\n" + name + r"\(", source)
    if match is None:
        raise ValueError(f"Missing XNU function: {name}")
    start = source.index("{", match.end())
    level = 1
    end = start + 1
    while level:
        level += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end]


def compile_probe(source: str, directory: Path) -> ctypes.CDLL:
    prefix = Path(__file__).with_name("text_fixup_probe.h").read_text()
    functions = ["cs_text_fixup_page", "cs_validate_hash", "cs_native4k_lazy_block", "cs_native4k_pass_run"]
    if "\ncs_text_fixup_hash(" in source:
        functions.insert(0, "cs_text_fixup_hash")
    program = directory / "probe.c"
    pass_start = source.index("struct cs_native4k_pass {")
    pass_end = source.index("\n};", pass_start) + 3
    program.write_text(prefix + source[pass_start:pass_end] + "\n".join(function(source, name) for name in functions) + r'''
void configure(const char *name, uint64_t offset, const void *original, const void *replacement, uint32_t length) {
    assert(length && length <= CS_TEXT_FIXUP_BYTES);
    cs_text_fixup_count = 1;
    memset(cs_text_fixups, 0, sizeof(cs_text_fixups));
    strncpy(cs_text_fixups[0].name, name, sizeof(cs_text_fixups[0].name) - 1);
    cs_text_fixups[0].offset = offset;
    cs_text_fixups[0].length = length;
    memcpy(cs_text_fixups[0].original, original, length);
    memcpy(cs_text_fixups[0].replacement, replacement, length);
}
int apply(const char *name, uint64_t offset, void *data) {
    struct vnode vp = { .v_name = name };
    return (int)cs_text_fixup_page(&vp, offset, data);
}
int validate(const char *name, uint64_t offset, const void *data, size_t length, const void *digest, int lazy) {
    struct vnode vp = { .v_name = name };
    CS_CodeDirectory cd = { .codeLimit = htonl((uint32_t)length) };
    struct cs_blob blob = { .csb_base_offset = (off_t)offset, .csb_end_offset = 16384,
        .csb_mem_kaddr = (void *)&cd, .csb_mem_size = sizeof(cd), .csb_cd = &cd,
        .csb_hashtype = &sha256, .csb_hash_pageshift = 14,
        .csb_native4k_hashes = digest, .csb_native4k_hash_count = 1, .csb_native4k_hashes_size = 32,
        .csb_native4k_lazy = lazy ? &fixture_lazy : NULL };
    memcpy(expected_digest, digest, 32);
    vm_size_t processed = 0;
    unsigned tainted = 0;
    return cs_validate_hash(&blob, &vp, offset, data, &processed, &tainted) && !(tainted & CS_VALIDATE_TAINTED);
}
int authenticate(const char *name, uint64_t offset, const void *data, size_t length, const void *digest, void *derived) {
    assert(length && length <= 16384);
    struct vnode vp = { .v_name = name };
    CS_CodeDirectory cd = { .codeLimit = htonl((uint32_t)length) };
    struct cs_blob blob = { .csb_base_offset = (off_t)offset, .csb_mem_kaddr = (void *)&cd,
        .csb_mem_size = sizeof(cd), .csb_cd = &cd, .csb_hashtype = &sha256, .csb_native4k_lazy = &fixture_lazy };
    fixture_bytes = data;
    fixture_base = offset;
    fixture_length = length;
    fixture_ready = 0;
    memcpy(expected_digest, digest, 32);
    memset(recorded_hashes, 0, sizeof(recorded_hashes));
    int status = cs_native4k_lazy_block(&vp, &blob, 0);
    memcpy(derived, recorded_hashes, sizeof(recorded_hashes));
    return status == KERN_SUCCESS && fixture_ready;
}
int authenticate_eager(const char *name, uint64_t offset, const void *data, size_t length, const void *digest, void *derived) {
    assert(length && length <= 16384);
    struct vnode vp = { .v_name = name };
    CS_CodeDirectory cd = { .codeLimit = htonl((uint32_t)length) };
    struct cs_blob blob = { .csb_base_offset = (off_t)offset, .csb_mem_kaddr = (void *)&cd,
        .csb_mem_size = sizeof(cd), .csb_cd = &cd, .csb_hashtype = &sha256 };
    struct cs_native4k_pass pass = { .vp = &vp, .blob = &blob, .cd = &cd, .md = &sha256,
        .storage = (uintptr_t)derived, .limit = length };
    fixture_bytes = data;
    fixture_base = offset;
    fixture_length = length;
    memcpy(expected_digest, digest, 32);
    memset(derived, 0, 128);
    cs_native4k_pass_run(&pass);
    return pass.error == 0;
}
''')
    library = directory / "probe.so"
    command = [os.environ.get("CC", "cc"), "-std=c11", "-shared", "-fPIC", "-O1", "-g",
               "-Wall", "-Wextra", "-Werror", "-Wno-deprecated-declarations",
               "-Wno-format", "-Wno-unused-parameter", "-Wno-unused-function",
               "-fsanitize=undefined", str(program), "-o", str(library)]
    if sys.platform != "darwin":
        command += ["-lcrypto"]
    subprocess.run(command, check=True)
    lib = ctypes.CDLL(str(library))
    lib.configure.argtypes = [ctypes.c_char_p, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
    lib.apply.argtypes = [ctypes.c_char_p, ctypes.c_uint64, ctypes.c_void_p]
    lib.validate.argtypes = [ctypes.c_char_p, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_size_t,
                            ctypes.c_void_p, ctypes.c_int]
    lib.authenticate.argtypes = [ctypes.c_char_p, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_size_t,
                                ctypes.c_void_p, ctypes.c_void_p]
    lib.authenticate_eager.argtypes = lib.authenticate.argtypes
    return lib


class TextFixupTest(unittest.TestCase):
    name = b"dyld_shared_cache_arm64e.03"
    base = 0x5DE0000
    original = bytes((i * 37 + i // 11) & 255 for i in range(16384))
    replacement = b"\x1f\x20\x03\xd5"

    def setUp(self):
        self.offset = self.base + 0x1134
        self.lib.configure(self.name, self.offset, self.original[0x1134:0x1138], self.replacement, 4)

    def modified(self):
        value = ctypes.create_string_buffer(self.original, 16384)
        page = ctypes.byref(value, 4096)
        self.assertEqual(self.lib.apply(self.name, self.base + 4096, page), 1)
        self.assertEqual(self.lib.apply(self.name, self.base + 4096, page), 0)
        return value

    def check_page(self, value, accepted, name=None, base=None):
        for lazy in (0, 1):
            self.assertEqual(bool(self.lib.validate(name or self.name, base or self.base + 4096,
                             ctypes.byref(value, 4096), 4096, hashlib.sha256(self.original[4096:8192]).digest(), lazy)), accepted)

    def check_block(self, value, accepted, name=None, base=None, length=16384):
        for authenticate in (self.lib.authenticate, self.lib.authenticate_eager):
            derived = ctypes.create_string_buffer(128)
            before = value.raw
            self.assertEqual(bool(authenticate(name or self.name, base or self.base, value, length,
                             hashlib.sha256(self.original[:length]).digest(), derived)), accepted)
            self.assertEqual(value.raw, before, "Validation must not restore executable pages")
            if accepted:
                for page in range((length + 4095) // 4096):
                    self.assertEqual(derived.raw[page * 32:(page + 1) * 32],
                                     hashlib.sha256(self.original[page * 4096:min(length, (page + 1) * 4096)]).digest())

    def test_revalidate_resident_patched_page(self):
        value = self.modified()
        self.assertNotEqual(hashlib.sha256(value.raw).digest(), hashlib.sha256(self.original).digest())
        self.check_page(value, True)
        self.check_block(value, True)

    def test_reclaimed_page_then_reapply(self):
        for _ in range(3):
            raw = ctypes.create_string_buffer(self.original, 16384)
            self.check_page(raw, True)
            self.check_block(raw, True)
            self.check_page(self.modified(), True)

    def test_unrelated_byte_changes_are_rejected(self):
        for index in (0, 4096, 0x1133, 0x1138, 16383):
            value = self.modified()
            value[index] = bytes([value.raw[index] ^ 1])
            self.check_block(value, False)
            if 4096 <= index < 8192:
                self.check_page(value, False)

    def test_inexact_replacement_is_rejected(self):
        value = self.modified()
        value[0x1135] = b"\xff"
        self.check_page(value, False)
        self.check_block(value, False)

    def test_wrong_vnode_and_offset_are_rejected(self):
        value = self.modified()
        self.check_page(value, False, name=b"another-cache")
        self.check_block(value, False, name=b"another-cache")
        self.check_page(value, False, base=self.base + 8192)
        self.check_block(value, False, base=self.base + 4096)

    def test_offset_above_4gib(self):
        high = 0x100000000 + self.base
        self.lib.configure(self.name, high + 0x1134, self.original[0x1134:0x1138], self.replacement, 4)
        value = ctypes.create_string_buffer(self.original, 16384)
        self.assertEqual(self.lib.apply(self.name, high + 4096, ctypes.byref(value, 4096)), 1)
        self.check_page(value, True, base=high + 4096)
        self.check_block(value, True, base=high)

    def test_snapshot_boundary_and_partial_last_page(self):
        for at in (0, 255, 4096 - 16, 8192, 16384 - 16):
            self.lib.configure(self.name, self.base + at, self.original[at:at + 16], b"R" * 16, 16)
            value = ctypes.create_string_buffer(self.original, 16384)
            self.assertEqual(self.lib.apply(self.name, self.base + (at & ~4095),
                                           ctypes.byref(value, at & ~4095)), 1)
            self.check_block(value, True)
            self.check_block(value, True, length=at + 16)

    def test_wrapping_or_outside_fixup_is_ignored(self):
        for offset in (self.base - 1, self.base + 16384, (1 << 64) - 2):
            self.lib.configure(self.name, offset, b"ABCD", self.replacement, 4)
            value = ctypes.create_string_buffer(self.original, 16384)
            self.check_block(value, True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--baseline-source", type=Path,
                        help="Also prove that the unpatched XNU functions reject their own fixup")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="text-fixup-") as temporary:
        directory = Path(temporary)
        TextFixupTest.lib = compile_probe(args.source.read_text(), directory)
        if args.baseline_source:
            baseline = directory / "baseline"
            baseline.mkdir()
            old = compile_probe(args.baseline_source.read_text(), baseline)
            original = TextFixupTest.original
            value = ctypes.create_string_buffer(original, 16384)
            old.configure(TextFixupTest.name, TextFixupTest.base + 0x1134, original[0x1134:0x1138],
                          TextFixupTest.replacement, 4)
            assert old.apply(TextFixupTest.name, TextFixupTest.base + 4096, ctypes.byref(value, 4096)) == 1
            assert old.validate(TextFixupTest.name, TextFixupTest.base + 4096, ctypes.byref(value, 4096),
                                4096, hashlib.sha256(original[4096:8192]).digest(), 1) == 0
            assert old.authenticate(TextFixupTest.name, TextFixupTest.base, value, 16384,
                                    hashlib.sha256(original).digest(), ctypes.create_string_buffer(128)) == 0
            assert old.authenticate_eager(TextFixupTest.name, TextFixupTest.base, value, 16384,
                                          hashlib.sha256(original).digest(), ctypes.create_string_buffer(128)) == 0
            print("Reproduced - upstream rejects its own fixup in 4 KiB and 16 KiB validation", flush=True)
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TextFixupTest))
        return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
