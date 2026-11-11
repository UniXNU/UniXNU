#!/usr/bin/env python3
"""Wrap tools/sweet-init.S into a static, ad-hoc signed arm64 Mach-O executable.

  mkinit.py OBJECT OUT [ENTITLEMENTS.plist]   (OBJECT: clang -target arm64-apple-ios16.0 -c sweet-init.S)

No available linker produces static iOS executables on Linux, and the program
is a single position-independent __text section, so the executable is laid
out here directly:

  __PAGEZERO  0 .. 4G, no access
  __TEXT      0x100000000, r-x, file 0..16K: header, load commands, code
  __LINKEDIT  0x100004000, r--: the code signature
  LC_UNIXTHREAD pc=_start (sp=0 -> the kernel provides the default user stack)
  LC_CODE_SIGNATURE ad-hoc SHA-256 CodeDirectory over __TEXT (4K pages)

A DEVELOPMENT kernel accepts static arm64 executables; mach_loader still
requires a code signature when code-signing enforcement is on.
"""
import hashlib, struct, sys

MH_MAGIC_64, CPU_TYPE_ARM64, MH_EXECUTE, MH_NOUNDEFS = 0xfeedfacf, 0x0100000c, 2, 1
LC_SEGMENT_64, LC_SYMTAB, LC_UNIXTHREAD, LC_CODE_SIGNATURE = 0x19, 0x2, 0x5, 0x1d
ARM_THREAD_STATE64, ARM_THREAD_STATE64_COUNT = 6, 68
VM_PROT_R, VM_PROT_X = 1, 4
S_ATTR_CODE = 0x80000400		# PURE_INSTRUCTIONS | SOME_INSTRUCTIONS
BASE, SEG = 0x100000000, 0x4000		# arm64 user segments are 16K aligned
CODE_OFF = 0x400			# after the load commands
CS_PAGE_SHIFT = 12
IDENT = b'org.sweet.init\0'


def text_of(obj):
    """Return (__text bytes, _start offset); refuse anything that needs linking."""
    magic, cpu, _, ftype, ncmds, _, _, _ = struct.unpack_from('<8I', obj, 0)
    assert magic == MH_MAGIC_64 and cpu == CPU_TYPE_ARM64 and ftype == 1, 'not an arm64 object'
    text, symtab, off = None, None, 32
    for _ in range(ncmds):
        cmd, size = struct.unpack_from('<II', obj, off)
        if cmd == LC_SEGMENT_64:
            nsects, = struct.unpack_from('<I', obj, off + 64)
            for i in range(nsects):
                s = off + 72 + 80 * i
                sect, seg = (obj[s + k:s + k + 16].split(b'\0')[0].decode() for k in (0, 16))
                _, ssize, soff, _, _, nreloc = struct.unpack_from('<QQIIII', obj, s + 32)
                assert nreloc == 0, f'{seg},{sect} has relocations: code must be position independent'
                if (seg, sect) == ('__TEXT', '__text'):
                    text = obj[soff:soff + ssize]
                else:
                    assert ssize == 0, f'unexpected non-empty section {seg},{sect}'
        elif cmd == LC_SYMTAB:
            symtab = struct.unpack_from('<4I', obj, off + 8)
        off += size
    assert text is not None and symtab, 'no __text or symbol table'
    symoff, nsyms, stroff, _ = symtab
    for i in range(nsyms):
        strx, ntype, _, _, value = struct.unpack_from('<IBBHQ', obj, symoff + 16 * i)
        if obj[stroff + strx:].split(b'\0')[0] == b'_start' and ntype & 1:	# N_EXT
            return bytes(text), value
    raise SystemExit('no global _start')


def segment(name, vmaddr, vmsize, fileoff, filesize, prot, sections=()):
    cmd = struct.pack('<II16sQQQQIIII', LC_SEGMENT_64, 72 + 80 * len(sections), name.encode(),
                      vmaddr, vmsize, fileoff, filesize, prot, prot, len(sections), 0)
    return cmd + b''.join(sections)


def code_signature(image, code_limit, text_size, entitlements=None):
    """SuperBlob holding one ad-hoc CodeDirectory (version 0x20400) over image[:code_limit],
    plus an XML entitlements blob (special slot 5) when entitlements (plist bytes) are given."""
    page = 1 << CS_PAGE_SHIFT
    hashes = b''.join(hashlib.sha256(image[o:min(o + page, code_limit)]).digest()
                      for o in range(0, code_limit, page))
    nslots = len(hashes) // 32
    ent_blob = None
    nspecial = 0
    if entitlements is not None:
        ent_blob = struct.pack('>II', 0xfade7171, 8 + len(entitlements)) + entitlements
        nspecial = 5			# slots -5..-1; only -5 (entitlements) is non-zero
        hashes = hashlib.sha256(ent_blob).digest() + bytes(32 * 4) + hashes
    hdr_len = 88				# fields through execSegFlags
    ident_off = hdr_len
    hash_off = ident_off + len(IDENT) + 32 * nspecial
    cd_len = ident_off + len(IDENT) + len(hashes)
    cd = struct.pack('>9I4BI', 0xfade0c02, cd_len, 0x20400, 0x2,	# CS_ADHOC
                     hash_off, ident_off, nspecial, nslots, code_limit,
                     32, 2, 0, CS_PAGE_SHIFT, 0)			# SHA-256, 4K pages
    cd += struct.pack('>III', 0, 0, 0)		# scatterOffset, teamOffset, spare3
    cd += struct.pack('>QQQQ', 0, 0, text_size, 1)	# codeLimit64, execSeg base/limit, MAIN_BINARY
    assert len(cd) == hdr_len
    cd += IDENT + hashes
    if ent_blob is None:
        sb_hdr = 12 + 8
        return struct.pack('>3I', 0xfade0cc0, sb_hdr + len(cd), 1) + struct.pack('>II', 0, sb_hdr) + cd
    sb_hdr = 12 + 8 * 2
    return (struct.pack('>3I', 0xfade0cc0, sb_hdr + len(cd) + len(ent_blob), 2) +
            struct.pack('>IIII', 0, sb_hdr, 5, sb_hdr + len(cd)) + cd + ent_blob)


def build(obj, entitlements=None):
    code, start = text_of(obj)
    assert CODE_OFF + len(code) <= SEG, 'code does not fit in one __TEXT page'
    sect = struct.pack('<16s16sQQIIIIIIII', b'__text', b'__TEXT', BASE + CODE_OFF, len(code),
                       CODE_OFF, 3, 0, 0, S_ATTR_CODE, 0, 0, 0)
    # The signature length depends only on the (fixed) __TEXT size: compute it first.
    sig_size = len(code_signature(bytes(SEG), SEG, SEG, entitlements))
    thread = struct.pack('<IIII', LC_UNIXTHREAD, 16 + 4 * ARM_THREAD_STATE64_COUNT,
                         ARM_THREAD_STATE64, ARM_THREAD_STATE64_COUNT)
    state = [0] * 33				# x0..x28, fp, lr, sp, pc
    state[32] = BASE + CODE_OFF + start
    thread += struct.pack('<33QII', *state, 0, 0)	# cpsr, pad
    cmds = [
        segment('__PAGEZERO', 0, BASE, 0, 0, 0),
        segment('__TEXT', BASE, SEG, 0, SEG, VM_PROT_R | VM_PROT_X, [sect]),
        segment('__LINKEDIT', BASE + SEG, SEG, SEG, sig_size, VM_PROT_R),
        thread,
        struct.pack('<4I', LC_CODE_SIGNATURE, 16, SEG, sig_size),
    ]
    lc = b''.join(cmds)
    header = struct.pack('<8I', MH_MAGIC_64, CPU_TYPE_ARM64, 0, MH_EXECUTE, len(cmds), len(lc),
                         MH_NOUNDEFS, 0)
    assert 32 + len(lc) <= CODE_OFF
    image = bytearray(SEG)
    image[:32 + len(lc)] = header + lc
    image[CODE_OFF:CODE_OFF + len(code)] = code
    sig = code_signature(bytes(image), SEG, SEG, entitlements)
    assert len(sig) == sig_size
    return bytes(image) + sig


if __name__ == '__main__':
    # mkinit.py OBJ OUT [ENTITLEMENTS.plist]
    ents = open(sys.argv[3], 'rb').read() if len(sys.argv) > 3 else None
    out = build(open(sys.argv[1], 'rb').read(), ents)
    open(sys.argv[2], 'wb').write(out)
    print(f'{sys.argv[2]}: {len(out)} bytes')
