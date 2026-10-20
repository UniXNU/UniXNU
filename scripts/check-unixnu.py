#!/usr/bin/env python3
"""Offline self-test of the unixnu build driver: defconfig parsing and module precedence."""
import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import io
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, HTTPServer

from unixnu import cli, feeds, ipsw, payload
from unixnu.config import Context, parse_config
from unixnu.util import Error


def expect(condition, message):
    if not condition:
        raise SystemExit(f'FAIL: {message}')


class RangeHandler(BaseHTTPRequestHandler):
    body = b''

    def log_message(self, *args):
        pass

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Length', str(len(self.body)))
        self.end_headers()

    def do_GET(self):
        start, end = self.headers['Range'].split('=')[1].split('-')
        chunk = self.body[int(start):int(end) + 1]
        self.send_response(206)
        self.send_header('Content-Length', str(len(chunk)))
        self.end_headers()
        self.wfile.write(chunk)


def der(tag, body):
    length = len(body)
    head = bytes([tag, length]) if length < 128 else bytes([tag, 0x82]) + length.to_bytes(2, 'big')
    return head + body


def main():
    config = parse_config('# c\nCONFIG_A=y\nCONFIG_B=n\n# CONFIG_C is not set\nCONFIG_D="x y"\nCONFIG_E=0x10\n')
    expect(config == {'A': True, 'B': False, 'C': False, 'D': 'x y', 'E': 16}, 'defconfig values')
    for raw, value in (
        ('0', 0), ('-0', 0), ('00', 0), ('-00', 0),
        ('8', 8), ('-8', -8), ('08', 8), ('-08', -8),
        ('010', 10), ('-010', -10), ('00042', 42), ('-00042', -42),
        ('0x10', 16), ('-0x10', -16), ('0x00FF', 255), ('-0x00FF', -255),
    ):
        expect(parse_config(f'CONFIG_NUMBER={raw}\n') == {'NUMBER': value}, f'defconfig number: {raw}')
    try:
        parse_config('CONFIG_A=maybe\n')
        expect(False, 'bad defconfig value accepted')
    except Error:
        pass
    with tempfile.TemporaryDirectory() as name:
        root = Path(name)
        for path in ('dev/drivers/Both', 'dev/drivers/DevOnly', 'loc/drivers/Both', 'loc/drivers/LocOnly', 'kd/Both', 'one/Both'):
            (root / path).mkdir(parents=True)
        (root / 'dev/board.toml').write_text('[board]\nname = "t"\n')
        parsed = cli.parser().parse_args(['status', '-D', str(root / 'dev'), '--out', str(root / 'out')])
        ctx = Context(parsed)
        found = feeds.resolve(ctx)
        expect(found[('driver', 'Both')].origin == 'device', 'device beats base')
        expect(('driver', 'ArmCpu') in found and found[('driver', 'ArmCpu')].origin == 'base', 'base modules found')
        parsed = cli.parser().parse_args(['status', '-D', str(root / 'dev'), '--out', str(root / 'out'), '--local', str(root / 'loc')])
        found = feeds.resolve(Context(parsed))
        expect(found[('driver', 'Both')].origin == 'local (--local)' and ('driver', 'LocOnly') in found, '--local beats device')
        parsed = cli.parser().parse_args(['status', '-D', str(root / 'dev'), '--out', str(root / 'out'), '--local', str(root / 'loc'),
                                          '--local-drivers', str(root / 'kd')])
        found = feeds.resolve(Context(parsed))
        expect(found[('driver', 'Both')].origin == 'local (--local-drivers)', '--local-drivers beats --local')
        parsed = cli.parser().parse_args(['status', '-D', str(root / 'dev'), '--out', str(root / 'out'), '--local', str(root / 'loc'),
                                          '--local-drivers', str(root / 'kd'), '--local-module', f'Both={root / "one"}'])
        found = feeds.resolve(Context(parsed))
        expect(found[('driver', 'Both')].origin == 'local (--local-module)', '--local-module wins')
        try:
            feeds.resolve(Context(cli.parser().parse_args(['status', '-D', str(root / 'dev'), '--out', str(root / 'out'),
                                                            '--local', str(root / 'missing')])))
            expect(False, 'missing --local directory accepted')
        except Error:
            pass
    expect(payload.check_args(['-v', 'a=1', 'b=x,y']) == '-v a=1 b=x,y', 'kernel arguments')
    for bad in (['a b'], ['x' * 1100], ['a;b']):
        try:
            payload.check_args(bad)
            expect(False, f'bad kernel argument accepted: {bad[0][:10]}')
        except Error:
            pass
    with tempfile.TemporaryDirectory() as name:
        root = Path(name)
        stage = root / 'stage/EFI/UniXNU'
        stage.mkdir(parents=True)
        (stage / 'unixnu.toml').write_text('version = 1\n')
        import os
        for path in (root / 'stage', *(root / 'stage').rglob('*')):
            os.utime(path, (payload.EPOCH, payload.EPOCH))
        payload.write_volume(root / 'stage', root / 'a.img', 'TEST', 64)
        payload.write_volume(root / 'stage', root / 'b.img', 'TEST', 64)
        expect((root / 'a.img').read_bytes() == (root / 'b.img').read_bytes(), 'payload volume is reproducible')
    # An IPSW is read member by member over HTTP range requests, and an IM4P payload is found by its DER structure.
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('BuildManifest.plist', b'manifest' * 1000)
        z.writestr('big.bin', bytes(range(256)) * 40000)
    RangeHandler.body = archive.getvalue()
    server = HTTPServer(('127.0.0.1', 0), RangeHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    remote = zipfile.ZipFile(ipsw.RangeFile(f'http://127.0.0.1:{server.server_port}/x.ipsw', block=4096))
    expect(remote.read('big.bin') == bytes(range(256)) * 40000 and remote.read('BuildManifest.plist') == b'manifest' * 1000, 'remote zip members')
    server.shutdown()
    im4p = der(0x30, der(0x16, b'IM4P') + der(0x16, b'krnl') + der(0x16, b'ver') + der(0x04, b'bvx2payload') + der(0x30, b'\x02\x01\x01'))
    expect(ipsw.im4p_payload(im4p) == b'bvx2payload', 'IM4P payload')
    try:
        ipsw.im4p_payload(der(0x30, der(0x16, b'XXXX') + der(0x16, b'krnl') + der(0x16, b'v') + der(0x04, b'z')))
        expect(False, 'bad IM4P accepted')
    except Error:
        pass
    print('PASS: unixnu defconfig parsing, module precedence, payload helpers and IPSW access')


if __name__ == '__main__':
    main()
