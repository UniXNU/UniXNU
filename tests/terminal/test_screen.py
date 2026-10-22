import binascii
import importlib.util
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from urllib.request import urlopen
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import debug_screen as screen
spec = importlib.util.spec_from_file_location('screen_terminal', ROOT / 'scripts/debug_terminal.py')
terminal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(terminal)


def packet(pixels, offset=0, size=None, frame_id=3, flags=0, width=2, height=1, frame_crc=None):
    if size is None:
        size = len(pixels) - offset
    payload = pixels[offset:offset + size]
    header = screen.HEADER.pack(screen.MAGIC, frame_id, flags, width, height, len(pixels),
                                offset, size, binascii.crc32(payload),
                                binascii.crc32(pixels) if frame_crc is None else frame_crc, 0)
    return header[:40] + struct.pack('<I', binascii.crc32(header[8:40])) + payload


def stop_packet():
    header = screen.HEADER.pack(screen.MAGIC, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0)
    return header[:40] + struct.pack('<I', binascii.crc32(header[8:40]))


class Screen(unittest.TestCase):
    def test_every_usb_split_and_log_bytes_are_preserved(self):
        pixels = b'\0\xf8\xe0\x07'
        data = b'log before\n' + packet(pixels) + b'log after\n'
        for split in range(len(data) + 1):
            wire = screen.ScreenWire()
            a, first = wire.feed(data[:split])
            b, second = wire.feed(data[split:])
            self.assertEqual(a + b, b'log before\nlog after\n')
            self.assertEqual(first + second, [(3, 0, 2, 1, pixels)])
            self.assertFalse(wire.pending)

    def test_crc_reorder_loss_and_frame_integrity(self):
        pixels = b'\0\xf8\xe0\x07'
        damaged = bytearray(packet(pixels)); damaged[-1] ^= 1
        wire = screen.ScreenWire()
        self.assertEqual(wire.feed(damaged)[1], [])
        self.assertEqual(wire.errors, 1)
        wire = screen.ScreenWire()
        self.assertEqual(wire.feed(packet(pixels, offset=2, size=2))[1], [])
        self.assertIsNone(wire.frame)
        self.assertEqual(wire.feed(packet(pixels, size=2))[1], [])
        self.assertEqual(wire.feed(packet(pixels, offset=2, size=2))[1], [(3, 0, 2, 1, pixels)])
        wire = screen.ScreenWire()
        self.assertEqual(wire.feed(packet(pixels, frame_crc=0))[1], [])
        self.assertEqual(wire.errors, 1)

    def test_bad_header_stop_recovers_logs_without_pixel_leak(self):
        pixels = b'\0\xf8\xe0\x07'
        bad = bytearray(packet(pixels)); bad[40] ^= 1
        wire = screen.ScreenWire()
        self.assertEqual(wire.feed(b'prior\n' + bad), (b'prior\n', []))
        self.assertTrue(wire.quarantine)
        tail = b'GIULIA SCREEN: stopped\nGIULIA DEBUG: pong\n'
        self.assertEqual(wire.feed(stop_packet() + tail), (tail, []))
        self.assertFalse(wire.quarantine)
        self.assertEqual(wire.stops, 1)
        self.assertFalse(wire.pending)
        # A completed one-shot snapshot may also have a damaged last header;
        # the kernel's unconditional control record must precede PTY markers.
        wire.feed(bad)
        raw = screen.SHELL_BEGIN + b'root# ' + screen.SHELL_END
        self.assertEqual(wire.feed(stop_packet() + raw), (raw, []))
        self.assertFalse(wire.quarantine)

    def test_half_frame_stop_and_reconnect(self):
        pixels = b'\0\xf8\xe0\x07'
        wire = screen.ScreenWire()
        self.assertEqual(wire.feed(packet(pixels, size=2))[1], [])
        self.assertEqual(wire.feed(stop_packet() + b'pong\n'), (b'pong\n', []))
        self.assertIsNone(wire.frame)
        with tempfile.TemporaryDirectory() as directory:
            capture = terminal.Capture(Path(directory))
            capture.feed(packet(pixels)[:46])
            self.assertEqual(capture.screen_store.info['frames'], 0)
            capture.close()
            other = terminal.Capture(Path(directory))
            try:
                self.assertEqual(other.feed(b'reconnected\n'), 'reconnected\n')
                self.assertEqual(other.screen_store.info['frames'], 0)
            finally:
                other.close()

    def test_lost_payload_byte_never_leaks_shifted_binary_as_logs(self):
        pixels = b'\0\xf8\xe0\x07'
        wire = screen.ScreenWire()
        damaged = packet(pixels)[:-1] + packet(pixels, frame_id=4)
        self.assertEqual(wire.feed(damaged), (b'', []))
        self.assertTrue(wire.quarantine)
        self.assertEqual(wire.feed(stop_packet() + b'pong\n'), (b'pong\n', []))
        self.assertFalse(wire.quarantine)

    def test_pty_binary_magic_is_never_screen_data(self):
        raw = b'root# ' + screen.MAGIC + b'\xff' * 80 + b'\0\x1b[0m'
        data = screen.SHELL_BEGIN + raw + screen.SHELL_END + b'logs\n'
        for split in range(len(data) + 1):
            wire = screen.ScreenWire()
            a, frames_a = wire.feed(data[:split]); b, frames_b = wire.feed(data[split:])
            self.assertEqual(a + b, data)
            self.assertFalse(frames_a + frames_b)
            self.assertFalse(wire.errors)

    def test_dimension_caps_and_malformed_header_are_bounded(self):
        for width, height, flags, size in ((1265, 1, 0, 2), (1, 2781, 0, 2), (2, 1, 3, 4), (2, 1, 0, 1025)):
            header = screen.HEADER.pack(screen.MAGIC, 1, flags, width, height, width * height * 2,
                                        0, size, 0, 0, 0)
            header = header[:40] + struct.pack('<I', binascii.crc32(header[8:40]))
            wire = screen.ScreenWire()
            self.assertEqual(wire.feed(header + b'x' * 100000)[1], [])
            self.assertLessEqual(len(wire.pending), len(screen.MAGIC) - 1)
            self.assertEqual(wire.errors, 1)

    def test_configured_dimensions_survive_fragmented_packets_and_resolution_changes(self):
        wire = screen.ScreenWire()
        for frame_id, width, height in ((10, 1024, 2), (11, 1, 1920), (12, 316, 695)):
            pixels = bytes((i * 17 + 23) & 255 for i in range(width * height * 2))
            data = b''.join(packet(pixels, offset=offset, size=min(1024, len(pixels) - offset),
                                   frame_id=frame_id, width=width, height=height)
                            for offset in range(0, len(pixels), 1024))
            frames = []
            for offset in range(0, len(data), 257):
                logs, complete = wire.feed(data[offset:offset + 257])
                self.assertFalse(logs)
                frames.extend(complete)
            self.assertEqual(frames, [(frame_id, 0, width, height, pixels)])
            self.assertIsNone(wire.frame)
        self.assertEqual(wire.errors, 0)

    def test_png_accepts_configured_size_and_rejects_out_of_bounds_pixels(self):
        png = screen.rgb565_png(1024, 1, b'\0\xf8' * 1024)
        self.assertEqual(struct.unpack_from('>II', png, 16), (1024, 1))
        for width, height, pixels in ((1265, 1, b'\0\0' * 1265),
                                      (1, 2781, b'\0\0' * 2781),
                                      (1024, 1, b'\0\0' * 1023),
                                      (0, 1, b'')):
            with self.subTest(width=width, height=height), self.assertRaises(ValueError):
                screen.rgb565_png(width, height, pixels)

    def test_magic_inside_pixel_payload_and_multiple_live_frames(self):
        pixels = screen.MAGIC
        wire = screen.ScreenWire()
        data = packet(pixels, width=4) + b'between\n' + packet(pixels, width=4, frame_id=4)
        logs, frames = wire.feed(data)
        self.assertEqual(logs, b'between\n')
        self.assertEqual([f[0] for f in frames], [3, 4])

    def test_png_colors_and_snapshot_files(self):
        pixels = b'\0\xf8\xe0\x07'
        png = screen.rgb565_png(2, 1, pixels)
        self.assertTrue(png.startswith(b'\x89PNG\r\n\x1a\n'))
        offset, image = 8, bytearray()
        while offset < len(png):
            length = struct.unpack_from('>I', png, offset)[0]
            name, data = png[offset + 4:offset + 8], png[offset + 8:offset + 8 + length]
            crc = struct.unpack_from('>I', png, offset + 8 + length)[0]
            self.assertEqual(crc, binascii.crc32(name + data))
            if name == b'IDAT':image.extend(data)
            offset += length + 12
        self.assertEqual(zlib.decompress(image), b'\0\xff\0\0\0\xff\0')
        with tempfile.TemporaryDirectory() as directory:
            capture = terminal.Capture(Path(directory))
            try:
                text = capture.feed(b'hello\n' + packet(pixels, flags=1) + b'pong\n')
                self.assertEqual(text, 'hello\npong\n')
                self.assertEqual((capture.root / 'device-000.log').read_bytes(), b'hello\npong\n')
                self.assertEqual((capture.root / 'screens/latest.png').read_bytes(), png)
                self.assertEqual((capture.root / 'screens/screen-00000003.png').read_bytes(), png)
                capture.save('fake')
                self.assertEqual(json.loads((capture.root / 'session.json').read_text())['screen_frames'], 1)
            finally:
                capture.close()

    def test_live_viewer_updates_real_frames_and_has_no_placeholder_image(self):
        with tempfile.TemporaryDirectory() as directory:
            store = screen.ScreenStore(Path(directory) / 'screens')
            viewer = screen.ScreenViewer(store)
            try:
                try:
                    urlopen(viewer.url + 'frame.png')
                    self.fail('No real frame should return 404')
                except HTTPError as error:
                    self.assertEqual(error.code, 404)
                    error.close()
                with urlopen(viewer.url) as response:
                    html = response.read()
                    self.assertIn(b'/status', html)
                    self.assertIn(b'/frame.png', html)
                    self.assertIn(b'/control', html)
                    self.assertNotIn(b'__VIEWER_TOKEN__', html)
                store.receive((1, 0, 1, 1, b'\0\xf8'))
                with urlopen(viewer.url + 'frame.png') as response:first = response.read()
                store.receive((2, 0, 1, 1, b'\xe0\x07'))
                with urlopen(viewer.url + 'frame.png') as response:second = response.read()
                self.assertNotEqual(first, second)
                with urlopen(viewer.url + 'status') as response:self.assertEqual(json.load(response)['frames'], 2)
            finally:
                viewer.close()

    def test_last_frame_and_stop_state_follow_wire_order_in_one_read(self):
        pixels = b'\0\xf8\xe0\x07'
        for stopped in (True, False):
            with self.subTest(stopped=stopped), tempfile.TemporaryDirectory() as directory:
                capture = terminal.Capture(Path(directory))
                try:
                    data = packet(pixels) + stop_packet() if stopped else stop_packet() + packet(pixels)
                    self.assertEqual(capture.feed(data + b'pong\n'), 'pong\n')
                    info = json.loads((capture.root / 'screens/screen.json').read_text())
                    self.assertEqual(info['frames'], 1)
                    self.assertEqual(info['state'], 'screen transfer stopped; last frame retained' if stopped else 'live frame received')
                    self.assertEqual(info, capture.screen_store.info)
                    self.assertEqual(capture.feed(b'next log\n'), 'next log\n')
                    self.assertIsNone(capture.screen_wire.last_event)
                    self.assertEqual(capture.screen_store.info, info)
                finally:
                    capture.close()

    def test_screen_metadata_is_published_as_complete_atomic_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            store = screen.ScreenStore(Path(directory) / 'screens')
            store.receive((1, 0, 1, 1, b'\0\xf8'))
            destination = store.directory / 'screen.json'
            original_replace = Path.replace
            publications = []

            def observe_replacement(source, target):
                if source.name == 'screen.json.tmp':
                    # A concurrent file viewer still sees the complete previous
                    # metadata until the complete new metadata replaces it.
                    self.assertEqual(Path(target), destination)
                    self.assertEqual(json.loads(destination.read_text())['frame_id'], 1)
                    self.assertEqual(json.loads(source.read_text())['frame_id'], 2)
                    publications.append(source)
                return original_replace(source, target)

            with patch.object(Path, 'replace', autospec=True, side_effect=observe_replacement):
                store.receive((2, 0, 1, 1, b'\xe0\x07'))
            self.assertEqual(len(publications), 1)
            self.assertFalse(publications[0].exists())
            self.assertEqual(json.loads(destination.read_text())['frame_id'], 2)

    def test_live_command_preview_and_automatic_stop_on_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = terminal.Capture(Path(directory)); capture.preview = Mock(return_value='http://127.0.0.1:1234/')
            commands = terminal.Commands(capture, 'fake'); writes = []
            serial = SimpleNamespace(write=lambda data: writes.append(data) or len(data))
            try:
                self.assertIn('127.0.0.1', commands.accept('screen.start'))
                with terminal.stop_screen_session(serial, lambda: commands.screen_started):
                    commands.tick(serial)
                    self.assertTrue(commands.screen_started)
                self.assertEqual(writes, [b'screen.start\n', b'screen.stop\n'])
                for command in ('screen.start', 'screen.stop', 'screen.snapshot'):
                    self.assertEqual(terminal.wire_command(command), (command + '\n').encode())
                with self.assertRaises(ValueError):terminal.wire_command('screen.start\nping')
            finally:
                capture.close()

    @unittest.skipUnless(os.environ.get('GIULIA_SCREEN_FIXTURE'), 'C packet fixture supplied by screen test runner')
    def test_actual_c_sender_bytes_decode_with_logs_interleaved(self):
        data = Path(os.environ['GIULIA_SCREEN_FIXTURE']).read_bytes()
        wire = screen.ScreenWire(); logs, frames = bytearray(), []
        for offset in range(0, len(data), 257):
            text, complete = wire.feed(data[offset:offset + 257]); logs.extend(text); frames.extend(complete)
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0][:4], (7, 0, 316, 695))
        self.assertEqual(frames[0][4], bytes((i * 17 + 23) & 255 for i in range(316 * 695 * 2)))
        self.assertTrue(logs.startswith(b'kernel before\n') and logs.endswith(b'kernel after\n'))
        self.assertNotIn(screen.MAGIC, logs)
        self.assertEqual(wire.errors, 0)


if __name__ == '__main__':
    unittest.main()
