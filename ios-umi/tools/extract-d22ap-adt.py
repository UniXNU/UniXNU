#!/usr/bin/env python3
"""Fetch the iPhone X (D22AP) device tree from Apple's IPSW and unpack it.

  extract-d22ap-adt.py [OUT]          (default research/ipsw-x/d22ap.adt)

tools/mkadt.py copies /product from it (MobileGestalt identity). Only the
33 KB DeviceTree.d22ap.im4p is downloaded (tools/remotezip.py), not the IPSW.
The IM4P payload is LZFSE ("bvx2"): needs the pyliblzfse module, e.g.
  python3 -m venv ~/.local/share/ios-tools-venv
  ~/.local/share/ios-tools-venv/bin/pip install pyliblzfse
  ~/.local/share/ios-tools-venv/bin/python tools/extract-d22ap-adt.py
"""
import os, subprocess, sys, tempfile

IPSW = ('https://updates.cdn-apple.com/2025FallFCS/fullrestores/122-77006/'
        '1158E502-D76D-4226-AA06-ED5E30CD1111/iPhone10,3,iPhone10,6_16.7.16_20H392_Restore.ipsw')
MEMBER = 'Firmware/all_flash/DeviceTree.d22ap.im4p'
HERE = os.path.dirname(os.path.abspath(__file__))

try:
    import liblzfse
except ImportError:
    sys.exit('needs pyliblzfse (see the docstring)')

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '../research/ipsw-x/d22ap.adt')
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable, os.path.join(HERE, 'remotezip.py'), IPSW, MEMBER, tmp], check=True)
    im4p = open(os.path.join(tmp, MEMBER), 'rb').read()
start = im4p.find(b'bvx2')
if start < 0:
    sys.exit('no LZFSE payload in the IM4P')
adt = liblzfse.decompress(im4p[start:])
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, 'wb').write(adt)
print(f'{out}: {len(adt)} bytes')
