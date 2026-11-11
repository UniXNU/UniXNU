#!/usr/bin/env python3
"""Put a new kernel payload into an existing umi boot image (Android boot header v2).

  umi-swap-payload.py BASE.img PAYLOAD.bin OUT.img

tools/umi-boot-image.sh needs the shim's aarch64 cross gcc; without it, build the payload alone
(tools/mkadt.py + tools/mkpayload.py, as that script does) and swap it in here. The payload is the
image's ramdisk; the shim (kernel), the DTB and every other header field are kept, the DTB moves
to follow the new ramdisk's last page. Prints the boot-args found in the payload.
"""
import struct
import sys


def pages(n, ps):
    return (n + ps - 1) // ps


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    base = open(sys.argv[1], 'rb').read()
    payload = open(sys.argv[2], 'rb').read()
    if base[:8] != b'ANDROID!':
        sys.exit('not an Android boot image')
    ks, _, rs, _, ss, _, _, ps, hv = struct.unpack('<9I', base[8:44])
    if hv != 2 or ss != 0:
        sys.exit(f'expected header v2 with no second stage (v{hv}, second {ss})')
    dtb_size = struct.unpack('<I', base[1648:1652])[0]
    k_off = ps
    r_off = k_off + pages(ks, ps) * ps
    d_off = r_off + pages(rs, ps) * ps
    kernel = base[k_off:k_off + ks]
    dtb = base[d_off:d_off + dtb_size]
    if dtb[:4] != b'\xd0\x0d\xfe\xed':
        sys.exit('no DTB where the header says')

    hdr = bytearray(base[:ps])
    struct.pack_into('<I', hdr, 16, len(payload))
    out = bytearray(hdr)
    for blob in (kernel, payload, dtb):
        out += blob + b'\0' * (pages(len(blob), ps) * ps - len(blob))
    open(sys.argv[3], 'wb').write(out)
    print(f'{sys.argv[3]}: kernel {ks}, ramdisk {rs} -> {len(payload)} ({pages(rs, ps)} -> '
          f'{pages(len(payload), ps)} pages), dtb {dtb_size}')
    i = payload.find(b'rd=ufsroot0')
    if i >= 0:
        s = payload.rfind(b'\0', 0, i) + 1
        line = payload[s:payload.find(b'\0', i)].decode()
        print(f'boot-args ({len(line)}): {line}')


if __name__ == '__main__':
    main()
