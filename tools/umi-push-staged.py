#!/usr/bin/env python3
"""Push a staged tree to the phone through the kernel file server, one process.
  tools/umi-push-staged.py ROOT MODES.txt LOG   (run tools/umi-usbnet.sh first)
MODES.txt: "<octal> /path" lines (tar modes; macOS tar drops setuid when not root).
Dirs: MKDIR (existing ones untouched) + CHMOD to the tar mode for new ones.
Files: RM, PUT with the tar mode (setuid kept), CHMOD, GET back and compare.
Links: RM, LINK. Resumable: paths already verified in LOG are skipped."""
import os, socket, sys

HOST, PORT = '192.168.7.2', 2223


def conn():
    return socket.create_connection((HOST, PORT), timeout=60)


def reply(s):
    line = b''
    while not line.endswith(b'\n'):
        c = s.recv(1)
        if not c:
            raise IOError('closed')
        line += c
    return line.decode().strip()


def cmd(text, data=b''):
    s = conn()
    try:
        s.sendall(text.encode() + data)
        return reply(s)
    finally:
        s.close()


def get(path):
    s = conn()
    try:
        s.sendall(f'GET {path}\n'.encode())
        r = reply(s)
        if not r.startswith('OK'):
            return None
        n = int(r.split()[1])
        buf = bytearray()
        while len(buf) < n:
            c = s.recv(min(65536, n - len(buf)))
            if not c:
                raise IOError('short read')
            buf += c
        return bytes(buf)
    finally:
        s.close()


root, modes_f, log_f = sys.argv[1:4]
modes = {}
for line in open(modes_f):
    m, p = line.rstrip('\n').split(' ', 1)
    modes[p] = int(m, 8)
done = set()
if os.path.exists(log_f):
    done = {l.split(' ', 1)[1].rstrip('\n') for l in open(log_f) if l.startswith('OK ')}
log = open(log_f, 'a')
paths = []
for d, dirs, files in os.walk(root):
    for n in dirs + files:
        paths.append(os.path.join(d, n)[len(root):])
paths.sort()
fail = 0
for i, p in enumerate(paths):
    if p in done:
        continue
    lp = root + p
    try:
        if os.path.islink(lp):
            cmd(f'RM {p}\n')
            r = cmd(f'LINK {os.readlink(lp)} {p}\n')
            ok = r.startswith('OK')
        elif os.path.isdir(lp):
            mode = modes.get(p, 0o755) & 0o7777
            r = cmd(f'MKDIR {p} {mode:o}\n')
            if r.startswith('OK'):
                cmd(f'CHMOD {p} {mode:o}\n')
            ok = True
        else:
            data = open(lp, 'rb').read()
            mode = modes.get(p, os.stat(lp).st_mode) & 0o7777
            cmd(f'RM {p}\n')
            r = cmd(f'PUT {p} {mode:o} {len(data)}\n', data)
            if r.startswith('OK'):
                cmd(f'CHMOD {p} {mode:o}\n')
            ok = r.startswith('OK') and get(p) == data
    except Exception as e:
        ok, r = False, str(e)
    log.write(f'{"OK" if ok else "FAIL"} {p}\n' if ok else f'FAIL {p} {r}\n')
    log.flush()
    fail += not ok
    if i % 250 == 0:
        print(f'{i}/{len(paths)} fail={fail}', flush=True)
print(f'done {len(paths)} fail={fail}', flush=True)
sys.exit(1 if fail else 0)
