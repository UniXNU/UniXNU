#!/usr/bin/env python3
"""Check that ppm_to_png keeps every raster byte and rejects malformed PPM files."""
import importlib.util
from pathlib import Path
import struct
import sys
import tempfile
import zlib

source = Path(__file__).resolve().parents[1] / 'package' / 'Scripts' / 'qemu-run.py'
spec = importlib.util.spec_from_file_location('qemu_run', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
valid = [
    (b'P6\n1 1\n255\n', b'\x01\x02\x03', 1, 1),
    (b'P6\n2 1\n255\n', b'\x09\x0a\x0b\x0c\x0d\x20', 2, 1),
    (b'P6\n1 1\n255\n', b'#\x00\xff', 1, 1),
    (b'P6\n# size\n1 1\n255\n', b'abc', 1, 1),
    (b'P6 # magic\n1 1\n255\n', b'abc', 1, 1),
    (b'P6\n1 # width\n1\n255\n', b'abc', 1, 1),
    (b'P6\n1 2\n255\n', b'abcdef', 1, 2),
]
invalid = [b'', b'P3\n1 1\n255\nabc', b'P6\n0 1\n255\n',
           b'P6\n-1 1\n255\nabc', b'P6\n1 1\n65535\nabcdef',
           b'P6\n1 1\n255\nab', b'P6\n1 1\n255\nabcd']
passed = rejected = 0
with tempfile.TemporaryDirectory() as work:
    ppm, png = Path(work) / 'in.ppm', Path(work) / 'out.png'
    for index, (header, pixels, width, height) in enumerate(valid):
        ppm.write_bytes(header + pixels)
        try:
            module.ppm_to_png(ppm, png)
            data = png.read_bytes()
            assert data[:8] == b'\x89PNG\r\n\x1a\n'
            offset, compressed = 8, b''
            while offset < len(data):
                size = struct.unpack_from('>I', data, offset)[0]
                tag = data[offset + 4:offset + 8]
                body = data[offset + 8:offset + 8 + size]
                crc = struct.unpack_from('>I', data, offset + 8 + size)[0]
                assert crc == zlib.crc32(tag + body) & 0xffffffff
                if tag == b'IHDR':
                    assert struct.unpack('>IIBBBBB', body) == (width, height, 8, 2, 0, 0, 0)
                if tag == b'IDAT':
                    compressed += body
                offset += size + 12
            expected = b''.join(b'\0' + pixels[y*width*3:(y+1)*width*3] for y in range(height))
            assert zlib.decompress(compressed) == expected
            passed += 1
        except Exception as error:
            print('valid case', index + 1, 'FAIL', type(error).__name__)
    for index, data in enumerate(invalid):
        ppm.write_bytes(data)
        try:
            module.ppm_to_png(ppm, png)
        except ValueError:
            rejected += 1
        except Exception as error:
            print('invalid case', index + 1, 'wrong error', type(error).__name__)
    print(f'valid={passed}/{len(valid)} invalid_rejected={rejected}/{len(invalid)}')
sys.exit(0 if passed == len(valid) and rejected == len(invalid) else 1)
