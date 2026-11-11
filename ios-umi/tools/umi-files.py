#!/usr/bin/env python3
"""Files on the running phone (bsd/dev/sweet_files.c, TCP 192.168.7.2:2223 on ue0).

Run tools/umi-usbnet.sh first, so the Mac has 192.168.7.1 on the phone's
USB Ethernet interface. The kernel file server comes up with the USB gadget
(boot-arg sweetfiles=0 keeps it off); every changing request is followed by
a sync on the phone, so what this writes survives the next reset.

  tools/umi-files.py put LOCAL REMOTE [MODE]     (mode octal, default from LOCAL)
  tools/umi-files.py get REMOTE LOCAL
  tools/umi-files.py mkdir REMOTE [MODE]
  tools/umi-files.py link TARGET REMOTE          (symlink)
  tools/umi-files.py rm REMOTE
  tools/umi-files.py chmod REMOTE MODE
  tools/umi-files.py list REMOTE-DIR             (kernel 0204+: "d" dir, "l" link, "-" file)
"""
import os
import socket
import stat
import sys

HOST, PORT = '192.168.7.2', 2223


def conn():
    return socket.create_connection((os.environ.get('SWEET_FILES_HOST', HOST), PORT), timeout=30)


def reply(s):
    line = b''
    while not line.endswith(b'\n'):
        c = s.recv(1)
        if not c:
            raise SystemExit('connection closed without a reply')
        line += c
    line = line.decode().strip()
    if not line.startswith('OK'):
        raise SystemExit(f'phone: {line}')
    return line


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    cmd, args = argv[0], argv[1:]
    s = conn()
    if cmd == 'put':
        local, remote = args[0], args[1]
        mode = int(args[2], 8) if len(args) > 2 else stat.S_IMODE(os.stat(local).st_mode)
        data = open(local, 'rb').read()
        s.sendall(f'PUT {remote} {mode:o} {len(data)}\n'.encode() + data)
        print(remote, reply(s))
    elif cmd == 'get':
        s.sendall(f'GET {args[0]}\n'.encode())
        n = int(reply(s).split()[1])
        buf = bytearray()
        while len(buf) < n:
            chunk = s.recv(min(65536, n - len(buf)))
            if not chunk:
                raise SystemExit('short read')
            buf += chunk
        open(args[1], 'wb').write(buf)
        print(args[0], n, 'bytes ->', args[1])
    elif cmd == 'list':
        s.sendall(f'LIST {args[0]}\n'.encode())
        n = int(reply(s).split()[1])
        buf = bytearray()
        while len(buf) < n:
            chunk = s.recv(min(65536, n - len(buf)))
            if not chunk:
                raise SystemExit('short read')
            buf += chunk
        for line in sorted(buf.decode('utf-8', 'replace').splitlines(), key=lambda l: l.split(' ', 1)[1]):
            t, name = line.split(' ', 1)
            print({'4': 'd', '10': 'l', '8': '-'}.get(t, '?'), name)
    elif cmd in ('mkdir', 'link', 'rm', 'chmod'):
        verb = {'mkdir': 'MKDIR', 'link': 'LINK', 'rm': 'RM', 'chmod': 'CHMOD'}[cmd]
        if cmd == 'mkdir' and len(args) == 1:
            args = args + ['755']
        s.sendall(f'{verb} {" ".join(args)}\n'.encode())
        print(cmd, ' '.join(args), reply(s))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
