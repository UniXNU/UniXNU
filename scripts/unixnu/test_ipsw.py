#!/usr/bin/env python3
"""Exercise remote IPSW ranges against a local HTTP server with injected faults."""
import collections
import contextlib
import hashlib
import http.client
import http.server
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import MagicMock, patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unixnu import ipsw
from unixnu.util import Error


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_HEAD(self):
        self.server.calls['HEAD'] += 1
        status = self.server.head_status.popleft() if self.server.head_status else 200
        self.send_response(status)
        self.send_header('Content-Length', str(len(self.server.data)))
        self.end_headers()

    def do_GET(self):
        value = self.headers['Range']
        self.server.calls[value] += 1
        start, end = map(int, value.removeprefix('bytes=').split('-'))
        queue = self.server.faults.get(value)
        fault = queue.popleft() if queue else 'ok'
        status = 206 if not isinstance(fault, int) else fault
        body = self.server.data[start:end + 1]
        self.send_response(status)
        self.send_header('Content-Range', f'bytes {start + (fault == "range")}-{end}/{len(self.server.data)}')
        self.send_header('Content-Length', str(len(body) + (fault == 'length')))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body[:-1] if fault == 'short' else body)
        self.wfile.flush()
        self.close_connection = True


class RemoteRanges(unittest.TestCase):
    def setUp(self):
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as packed:
            packed.writestr('OS.dmg', bytes(range(256)) * 20)
        self.archive = archive.getvalue()
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.data = self.archive
        self.server.calls = collections.Counter()
        self.server.head_status = collections.deque()
        self.server.faults = {}
        self.thread = threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.01), daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}/restore.ipsw'
        self.sleep = self.enterContext(patch.object(ipsw.time, 'sleep'))
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def faults(self, key, *faults):
        self.server.faults[key] = collections.deque(faults)

    def test_truncated_range_retries_without_changing_zip_bytes(self):
        self.faults('bytes=0-127', 'short', 'ok')
        with ipsw.RangeFile(self.url, block=128) as stream:
            self.assertEqual(stream.read(128), self.archive[:128])
            self.assertEqual(stream.cache[0], self.archive[:128])
            stream.seek(0)
            self.assertEqual(stream.read(128), self.archive[:128])
            self.assertEqual(self.server.calls['bytes=0-127'], 2)
            with zipfile.ZipFile(stream) as packed:
                self.assertEqual(packed.read('OS.dmg'), bytes(range(256)) * 20)

    def test_incomplete_read_exception_is_retried(self):
        with ipsw.RangeFile(self.url, block=128) as stream:
            response = MagicMock(status=206, headers={'Content-Range': f'bytes 0-127/{len(self.archive)}',
                                                      'Content-Length': '128'})
            response.__enter__.return_value = response
            response.read.side_effect = [http.client.IncompleteRead(b'x', 127), self.archive[:128]]
            with patch.object(ipsw.urllib.request, 'urlopen', return_value=response) as opener:
                self.assertEqual(stream.read(128), self.archive[:128])
                self.assertEqual(opener.call_count, 2)
            self.assertEqual(stream.tell(), 128)

    def test_failed_range_does_not_enter_cache_or_advance_position(self):
        self.faults('bytes=0-127', 'short', 'short', 'short')
        with ipsw.RangeFile(self.url, block=128, retries=3) as stream:
            with self.assertRaisesRegex(Error, 'failed after 3 attempts'):
                stream.read(128)
            self.assertEqual(stream.tell(), 0)
            self.assertNotIn(0, stream.cache)
            self.assertEqual(self.server.calls['bytes=0-127'], 3)

    def test_retry_head_and_range_probe(self):
        self.server.head_status.extend((503, 200))
        self.faults('bytes=0-0', 'short', 'ok')
        with ipsw.RangeFile(self.url) as stream:
            self.assertEqual(stream.size, len(self.archive))
        self.assertEqual(self.server.calls['HEAD'], 2)
        self.assertEqual(self.server.calls['bytes=0-0'], 2)

    def test_mismatched_ranges_lengths_and_http_status_are_rejected(self):
        for fault in ('range', 'length', 200):
            with self.subTest(fault=fault):
                self.faults('bytes=0-127', fault, 'ok')
                with ipsw.RangeFile(self.url, block=128) as stream:
                    self.assertEqual(stream.read(128), self.archive[:128])

    def test_transient_http_error_is_retried(self):
        self.faults('bytes=0-127', 503, 'ok')
        with ipsw.RangeFile(self.url, block=128) as stream:
            self.assertEqual(stream.read(128), self.archive[:128])

    def test_permanent_http_error_is_reported_once(self):
        self.faults('bytes=0-127', 403)
        with ipsw.RangeFile(self.url, block=128) as stream:
            with self.assertRaisesRegex(Error, 'HTTP 403'):
                stream.read(128)
        self.assertEqual(self.server.calls['bytes=0-127'], 1)
        self.sleep.assert_not_called()

    def test_partial_extraction_is_not_published_and_valid_cache_is_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            source = ipsw.Ipsw.__new__(ipsw.Ipsw)
            source.cache = Path(directory)
            source.remote = True
            source.config = {'sha256': {'OS.dmg': hashlib.sha256(bytes(range(256)) * 20).hexdigest()}}
            source.info = lambda _component: ('OS.dmg', 5120, 0)
            source.zip = MagicMock()
            reader = source.zip.open.return_value.__enter__.return_value
            reader.read.side_effect = [b'partial', Error('network failure')]
            with self.assertRaisesRegex(Error, 'network failure'):
                source.extract('OS')
            self.assertFalse((source.cache / 'OS.dmg').exists())
            self.assertFalse((source.cache / 'OS.dmg.json').exists())
            with ipsw.RangeFile(self.url, block=128) as stream, zipfile.ZipFile(stream) as packed:
                source.zip = packed
                destination = source.extract('OS')
            self.assertEqual(destination.read_bytes(), bytes(range(256)) * 20)
            self.assertEqual(json.loads((source.cache / 'OS.dmg.json').read_text())['size'], 5120)
            source.zip = MagicMock()
            self.assertEqual(source.extract('OS'), destination)
            source.zip.open.assert_not_called()


if __name__ == '__main__':
    unittest.main()
