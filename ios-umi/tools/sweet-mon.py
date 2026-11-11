#!/usr/bin/env python3
"""Talk to the phone's UDP debug monitor (kernel 0115+, sweetusb=2).

  tools/sweet-mon.py 'r 0x1c00000 8'      read 8 words at a physical address
  tools/sweet-mon.py 'w 0x... 0x...'      write one word
  tools/sweet-mon.py 'wlan 4'             run the umi PCIe/QCA6390 bring-up to stage 4
Several commands may be given; each is sent and its reply printed.
"""
import socket, sys

PHONE = ('192.168.7.2', 5141)


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for cmd in sys.argv[1:]:
        s.settimeout(30 if cmd.startswith('wlan') else 3)
        s.sendto(cmd.encode(), PHONE)
        try:
            print(s.recv(2048).decode(errors='replace'), end='')
        except socket.timeout:
            print(f'{cmd}: no reply')
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
