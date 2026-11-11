#!/usr/bin/env python3
"""List or extract single members of a remote zip (e.g. an IPSW) via HTTP range requests.

  remotezip.py URL                      list members
  remotezip.py URL PATTERN OUTDIR       extract members whose name contains PATTERN

Members are streamed to disk in chunks (multi-GB DMGs never sit in RAM), a
partial download resumes from where it stopped, and the zip CRC-32 is
checked before the file gets its final name.
"""
import os, struct, subprocess, sys, zlib


# curl rather than urllib: urllib hangs on this host's broken IPv6 route to
# Apple's CDN, curl falls back to IPv4.
def curl(*args):
    return subprocess.run(['curl', '-sfL', '--max-time', '300', *args],
                          check=True, capture_output=True).stdout


def get(url, start, end):
    data = curl('-r', f'{start}-{end}', url)
    # A server ignoring Range would send the whole multi-GB file.
    assert len(data) == end - start + 1, f'bad range reply ({len(data)} bytes)'
    return data


def size_of(url):
    for line in curl('-I', url).decode().splitlines():
        if line.lower().startswith('content-length:'):
            return int(line.split(':')[1])
    raise RuntimeError('no Content-Length')


def central_dir(url):
    total = size_of(url)
    tail = get(url, max(0, total - 65536 - 22), total - 1)
    eocd = tail.rfind(b'PK\x05\x06')
    assert eocd >= 0, 'no EOCD'
    cd_size, cd_off = struct.unpack_from('<II', tail, eocd + 12)
    loc = tail.rfind(b'PK\x06\x06')	# zip64 EOCD record (IPSWs are >4GB)
    if loc >= 0:
        cd_size, cd_off = struct.unpack_from('<QQ', tail, loc + 40)
    cd = get(url, cd_off, cd_off + cd_size - 1)
    i, out = 0, []
    while i < len(cd) and cd[i:i + 4] == b'PK\x01\x02':
        method, = struct.unpack_from('<H', cd, i + 10)
        crc, csize, usize = struct.unpack_from('<III', cd, i + 16)
        nlen, xlen, clen = struct.unpack_from('<HHH', cd, i + 28)
        lho, = struct.unpack_from('<I', cd, i + 42)
        name = cd[i + 46:i + 46 + nlen].decode()
        extra = cd[i + 46 + nlen:i + 46 + nlen + xlen]
        j = 0
        while j < len(extra):	# zip64 extended info
            hid, hlen = struct.unpack_from('<HH', extra, j)
            if hid == 1:
                vals = list(struct.unpack_from('<%dQ' % (hlen // 8), extra, j + 4))
                if usize == 0xffffffff: usize = vals.pop(0)
                if csize == 0xffffffff: csize = vals.pop(0)
                if lho == 0xffffffff: lho = vals.pop(0)
            j += 4 + hlen
        out.append((name, method, csize, usize, lho, crc))
        i += 46 + nlen + xlen + clen
    return out


CHUNK = 64 << 20


def extract(url, entry, outdir):
    name, method, csize, usize, lho, crc = entry
    path = os.path.join(outdir, name)
    if name.endswith('/'):
        os.makedirs(path, exist_ok=True)
        return
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    if os.path.exists(path) and os.path.getsize(path) == usize:
        print(f'{name}: already complete')
        return
    hdr = get(url, lho, lho + 29)
    nlen, xlen = struct.unpack_from('<HH', hdr, 26)
    start = lho + 30 + nlen + xlen
    part = path + '.part'
    # Compressed members restart (no resumable inflate state); stored ones resume.
    done = os.path.getsize(part) if method == 0 and os.path.exists(part) else 0
    inflate = zlib.decompressobj(-15) if method == 8 else None
    with open(part, 'ab' if done else 'wb') as out:
        while done < csize:
            n = min(CHUNK, csize - done)
            data = get(url, start + done, start + done + n - 1)
            out.write(inflate.decompress(data) if inflate else data)
            done += n
            print(f'{name}: {done * 100 // csize}% ({done >> 20} MiB)', flush=True)
        if inflate:
            out.write(inflate.flush())
    with open(part, 'rb') as f:
        got = 0
        while chunk := f.read(CHUNK):
            got = zlib.crc32(chunk, got)
    assert os.path.getsize(part) == usize, (name, os.path.getsize(part), usize)
    assert got == crc, f'{name}: CRC-32 {got:08x} != {crc:08x}'
    os.replace(part, path)
    print(f'{name}: {usize} bytes, CRC-32 ok')


if __name__ == '__main__':
    url = sys.argv[1]
    entries = central_dir(url)
    if len(sys.argv) == 2:
        for e in entries:
            print(f'{e[3]:>12} {e[0]}')
    else:
        for e in entries:
            if sys.argv[2] in e[0]:
                extract(url, e, sys.argv[3])
