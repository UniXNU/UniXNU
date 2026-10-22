"""Bounded GSC1 stream decoder, PNG writer, and localhost live screen viewer."""
import binascii
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import re
import secrets
import struct
import threading
import time
import webbrowser
import zlib

MAGIC = b'\0GSC1\r\n\x1a'
HEADER = struct.Struct('<8sIIHHIIIIII')
MAX_WIDTH, MAX_HEIGHT = 1264, 2780
MAX_BYTES = MAX_WIDTH * MAX_HEIGHT * 2
MAX_CHUNK = 1024
SHELL_BEGIN = b'\r\nGIULIA SHELL BEGIN\r\n'
SHELL_END = b'\r\nGIULIA SHELL END\r\n'


class ScreenWire:
    """Remove screen packets before UTF-8/PTY parsing, preserving log bytes.

    Headers and payloads have separate CRCs. A malformed header enters bounded
    resynchronization: bytes are discarded until another verified screen header,
    rather than treating possible pixel bytes as terminal output.
    """
    def __init__(self):
        self.pending = bytearray()
        self.frame = None
        self.identity = None
        self.errors = 0
        self.quarantine = False
        self.shell = False
        self.stops = 0
        self.last_event = None

    def feed(self, data):
        self.last_event = None
        self.pending.extend(data)
        logs = bytearray()
        frames = []
        while self.pending:
            if self.shell:
                end = self.pending.find(SHELL_END)
                if end >= 0:
                    logs.extend(self.pending[:end + len(SHELL_END)])
                    del self.pending[:end + len(SHELL_END)]
                    self.shell = False
                    continue
                keep = 0
                for n in range(1, min(len(SHELL_END), len(self.pending) + 1)):
                    if self.pending[-n:] == SHELL_END[:n]:
                        keep = n
                ready = len(self.pending) - keep
                logs.extend(self.pending[:ready])
                del self.pending[:ready]
                break
            at = self.pending.find(MAGIC)
            shell_at = self.pending.find(SHELL_BEGIN) if not self.quarantine else -1
            if shell_at >= 0 and (at < 0 or shell_at < at):
                logs.extend(self.pending[:shell_at + len(SHELL_BEGIN)])
                del self.pending[:shell_at + len(SHELL_BEGIN)]
                self.shell = True
                continue
            if at < 0:
                keep = 0
                for marker in (MAGIC, SHELL_BEGIN) if not self.quarantine else (MAGIC,):
                    for n in range(1, min(len(marker), len(self.pending) + 1)):
                        if self.pending[-n:] == marker[:n]:
                            keep = max(keep, n)
                ready = len(self.pending) - keep
                if not self.quarantine:
                    logs.extend(self.pending[:ready])
                del self.pending[:ready]
                break
            if at:
                if not self.quarantine:
                    logs.extend(self.pending[:at])
                del self.pending[:at]
            if len(self.pending) < HEADER.size:
                break
            _, frame_id, flags, width, height, total, offset, size, crc, frame_crc, header_crc = HEADER.unpack_from(self.pending)
            control = flags == 2 and not any((width, height, total, offset, size, crc, frame_crc))
            valid = (frame_id and (control or (flags in (0, 1) and 1 <= width <= MAX_WIDTH and
                     1 <= height <= MAX_HEIGHT and total == width * height * 2 and
                     total <= MAX_BYTES and 1 <= size <= MAX_CHUNK and
                     offset <= total and size <= total - offset)) and
                     binascii.crc32(self.pending[8:40]) == header_crc)
            if not valid:
                self.errors += 1
                self.frame = self.identity = None
                self.quarantine = True
                del self.pending[0]
                continue
            if len(self.pending) < HEADER.size + size:
                break
            payload = bytes(self.pending[HEADER.size:HEADER.size + size])
            del self.pending[:HEADER.size + size]
            self.quarantine = False
            if control:
                self.frame = self.identity = None
                self.stops += 1
                self.last_event = 'stop'
                continue
            if binascii.crc32(payload) != crc:
                self.errors += 1
                self.frame = self.identity = None
                self.quarantine = True
                continue
            identity = (frame_id, flags, width, height, total, frame_crc)
            if offset == 0:
                self.identity, self.frame = identity, bytearray()
            if self.identity != identity or self.frame is None or offset != len(self.frame):
                self.errors += 1
                self.frame = self.identity = None
                continue
            self.frame.extend(payload)
            if len(self.frame) == total:
                if binascii.crc32(self.frame) == frame_crc:
                    frames.append((frame_id, flags, width, height, bytes(self.frame)))
                    self.last_event = 'frame'
                else:
                    self.errors += 1
                self.frame = self.identity = None
        return bytes(logs), frames


def rgb565_png(width, height, pixels):
    if not 1 <= width <= MAX_WIDTH or not 1 <= height <= MAX_HEIGHT or len(pixels) != width * height * 2:
        raise ValueError('Invalid screen dimensions/pixel length')
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)
        row = bytearray(width * 3)
        for x in range(width):
            n = 2 * (y * width + x)
            pixel = pixels[n] | pixels[n + 1] << 8
            r, g, b = (pixel >> 11) & 31, (pixel >> 5) & 63, pixel & 31
            row[x * 3] = (r << 3) | (r >> 2)
            row[x * 3 + 1] = (g << 2) | (g >> 4)
            row[x * 3 + 2] = (b << 3) | (b >> 2)
        scanlines.extend(row)
    def chunk(name, data):
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', binascii.crc32(name + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(scanlines, 3)) + chunk(b'IEND', b''))


class ScreenStore:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.lock = threading.Lock()
        self.png = None
        self.info = {'frames': 0, 'state': 'waiting for a real framebuffer frame'}

    def update(self, **fields):
        with self.lock:
            self.info.update(fields)

    def _publish_info_locked(self):
        self.directory.mkdir(exist_ok=True)
        temporary = self.directory / 'screen.json.tmp'
        temporary.write_text(json.dumps(self.info, indent=2), encoding='utf-8')
        temporary.replace(self.directory / 'screen.json')

    def set_state(self, state):
        with self.lock:
            self.info['state'] = state
            self._publish_info_locked()

    def receive(self, frame):
        frame_id, snapshot, width, height, pixels = frame
        png = rgb565_png(width, height, pixels)
        self.directory.mkdir(exist_ok=True)
        latest = self.directory / 'latest.png'
        temporary = self.directory / 'latest.tmp'
        temporary.write_bytes(png)
        temporary.replace(latest)
        if snapshot:
            (self.directory / f'screen-{frame_id:08x}.png').write_bytes(png)
        with self.lock:
            self.png = png
            self.info.update({'frames': self.info['frames'] + 1, 'frame_id': frame_id,
                         'width': width, 'height': height, 'snapshot': bool(snapshot),
                         'received_utc': datetime.now(timezone.utc).isoformat(),
                         'state': 'snapshot received' if snapshot else 'live frame received', 'latest_png': str(latest.resolve()),
                         'source': 'actual panel framebuffer, aspect-preserving point sampling, RGB565'})
            self._publish_info_locked()
        return latest


def _integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{label} must be an integer in {low}..{high}.')
    return value


def keyboard_usage(code):
    """KeyboardEvent.code to USB HID keyboard page; layout stays on the phone."""
    if isinstance(code, str) and re.fullmatch(r'Key[A-Z]', code):
        return ord(code[-1]) - ord('A') + 4
    if isinstance(code, str) and re.fullmatch(r'Digit[0-9]', code):
        return 39 if code[-1] == '0' else 29 + int(code[-1])
    if isinstance(code, str) and re.fullmatch(r'F(?:[1-9]|1[0-2])', code):
        return 57 + int(code[1:])
    special = {'Enter': 40, 'Escape': 41, 'Backspace': 42, 'Tab': 43, 'Space': 44,
               'Minus': 45, 'Equal': 46, 'BracketLeft': 47, 'BracketRight': 48,
               'Backslash': 49, 'Semicolon': 51, 'Quote': 52, 'Backquote': 53,
               'Comma': 54, 'Period': 55, 'Slash': 56, 'CapsLock': 57,
               'PrintScreen': 70, 'ScrollLock': 71, 'Pause': 72, 'Insert': 73,
               'Home': 74, 'PageUp': 75, 'Delete': 76, 'End': 77, 'PageDown': 78,
               'ArrowRight': 79, 'ArrowLeft': 80, 'ArrowDown': 81, 'ArrowUp': 82,
               'NumLock': 83, 'NumpadDivide': 84, 'NumpadMultiply': 85,
               'NumpadSubtract': 86, 'NumpadAdd': 87, 'NumpadEnter': 88,
               'Numpad0': 98, 'NumpadDecimal': 99, 'ContextMenu': 101,
               'ControlLeft': 224, 'ShiftLeft': 225, 'AltLeft': 226, 'MetaLeft': 227,
               'ControlRight': 228, 'ShiftRight': 229, 'AltRight': 230, 'MetaRight': 231}
    if isinstance(code, str) and re.fullmatch(r'Numpad[1-9]', code):
        return 88 + int(code[-1])
    try:
        return special[code]
    except (KeyError, TypeError):
        raise ValueError('Unsupported physical keyboard key.') from None


class ScreenControl:
    """Bounded UI mailbox. Only the terminal loop writes to the serial port.

    Input availability comes from the running kernel, never from a click. A UI
    heartbeat and the independent device lease release held input after a crash.
    """
    LIMIT = 128
    LEASE = 2.5

    def __init__(self, store):
        self.store = store
        self.lock = threading.Lock()
        self.queue = deque()
        self.connection = 'diagnostic'
        self.available = False
        self.capabilities = {'touch': False, 'keyboard': False, 'buttons': False}
        self.enabled = False
        self.last_client = 0
        self.next_keepalive = 0
        self.touch_active = False
        self.settings = {'max_size': 695, 'max_fps': 1, 'control': False}
        self._publish('Waiting for the device input capability report')

    def _publish(self, message=None):
        fields = dict(connection=self.connection, input_available=self.available,
                      input_capabilities=dict(self.capabilities), settings=dict(self.settings))
        if message is not None:
            fields['input_status'] = message
        self.store.update(**fields)

    def _release(self):
        self.queue = deque(c for c in self.queue if not c.startswith('input.'))
        if self.available and self.connection == 'diagnostic':
            self.queue.appendleft('input.release')
        self.touch_active = False

    def set_connection(self, connection):
        with self.lock:
            self.queue.clear()
            self.enabled = self.settings['control'] = False
            self.touch_active = False
            self.connection = connection
            self._publish('Control paused: ' + connection)

    def shutdown(self):
        self.set_connection('disconnected')

    def observe(self, line):
        with self.lock:
            if line.startswith('GIULIA INPUT:'):
                values = dict(re.findall(r'(available|touch|keyboard|buttons)=([01])\b', line))
                if 'available' in values:
                    self.available = values['available'] == '1'
                    self.capabilities = {k: values.get(k) == '1' for k in self.capabilities}
                    if not self.available:
                        self._release()
                        self.enabled = self.settings['control'] = False
                self._publish(line)
            elif line.startswith('GIULIA SCREEN:'):
                size = re.search(r'max_size=(\d+)', line)
                fps = re.search(r'max_fps=(\d+)', line)
                if size and fps:
                    self.settings.update(max_size=int(size[1]), max_fps=int(fps[1]))
                    self._publish()
                if 'unavailable' in line or 'requires ' in line or 'invalid' in line:
                    self.store.set_state(line)

    def request_status(self):
        with self.lock:
            if self.connection == 'diagnostic' and 'input.status' not in self.queue:
                if len(self.queue) < self.LIMIT:
                    self.queue.append('input.status')

    def handle(self, payload):
        if not isinstance(payload, dict) or not isinstance(payload.get('action'), str):
            raise ValueError('Expected a screen control action.')
        action = payload['action']
        with self.lock:
            if self.connection != 'diagnostic':
                raise ValueError('Screen controls are paused while ' + self.connection + '.')
            if action == 'control':
                enabled = payload.get('enabled')
                if type(enabled) is not bool:
                    raise ValueError('enabled must be a boolean.')
                if enabled and not self.available:
                    raise ValueError('Device input service has not reported ready; use a new GUI kernel.')
                if not enabled:
                    self._release()
                self.enabled = self.settings['control'] = enabled
                self.last_client = time.monotonic()
                self._publish('Desktop control enabled' if enabled else 'Desktop control disabled')
                return {'queued': True, 'enabled': enabled}
            if action == 'release':
                self._release()
                return {'queued': True}
            if action == 'heartbeat':
                if self.enabled:
                    self.last_client = time.monotonic()
                return {'queued': False}
            if action in ('start', 'stop', 'snapshot'):
                commands = ['screen.' + action]
                if action == 'start':
                    commands.append('input.status')
                if action == 'stop':
                    self._release()
                    self.enabled = self.settings['control'] = False
                    self._publish('Desktop control disabled')
            elif action == 'configure':
                size = _integer(payload.get('max_size'), 160, 2780, 'Maximum size')
                fps = _integer(payload.get('max_fps'), 1, 30, 'Maximum FPS')
                commands = [f'screen.configure {size} {fps}']
                # Drop obsolete pending changes, preserving input event order.
                self.queue = deque(c for c in self.queue if not c.startswith('screen.configure '))
            else:
                if not self.enabled or not self.available:
                    raise ValueError('Enable desktop control after the device input service is ready.')
                commands = self._input_commands(action, payload)
            coalesced = action == 'touch' and payload.get('phase') == 'move' and self.queue and self.queue[-1].startswith('input.touch move ')
            if len(self.queue) + (0 if coalesced else len(commands)) > self.LIMIT:
                self._release()
                self.enabled = self.settings['control'] = False
                self._publish('Input queue full; held input released. Enable control to retry.')
                raise ValueError('Screen input queue full; control paused and held input released.')
            if coalesced:
                self.queue[-1] = commands[0]
            else:
                self.queue.extend(commands)
            if action == 'touch':
                self.touch_active = payload['phase'] in ('down', 'move')
            if action in ('touch', 'key', 'scroll'):
                self.last_client = time.monotonic()
            return {'queued': True, 'commands': len(commands)}

    def _input_commands(self, action, payload):
        if action in ('touch', 'scroll'):
            if not self.capabilities['touch']:
                raise ValueError('The device touch input service is unavailable.')
            x = _integer(payload.get('x'), 0, 65535, 'Touch X')
            y = _integer(payload.get('y'), 0, 65535, 'Touch Y')
            if action == 'touch':
                phase = payload.get('phase')
                if phase not in ('down', 'move', 'up', 'cancel'):
                    raise ValueError('Unknown touch phase.')
                if phase == 'down' and self.touch_active:
                    raise ValueError('A pointer gesture is already active.')
                if phase == 'move' and not self.touch_active:
                    raise ValueError('A pointer gesture must start with down.')
                return [f'input.touch {phase} {x} {y}']
            if self.touch_active:
                raise ValueError('Finish the pointer drag before scrolling.')
            dx, dy = payload.get('delta_x', 0), payload.get('delta_y', 0)
            if any(type(n) not in (int, float) or not math.isfinite(n) or abs(n) > 10000 for n in (dx, dy)):
                raise ValueError('Scroll deltas must be finite and within 10000.')
            # A wheel scroll is a bounded single-finger swipe. Device input is
            # serialized at 100Hz rather than sleeping inside an HTTP handler.
            end_x = max(0, min(65535, x - round(dx * 80)))
            end_y = max(0, min(65535, y - round(dy * 80)))
            return [f'input.touch down {x} {y}', *[
                f'input.touch move {round(x + (end_x-x)*i/6)} {round(y + (end_y-y)*i/6)}'
                for i in range(1, 7)], f'input.touch up {end_x} {end_y}']
        if action == 'key':
            pressed = payload.get('pressed')
            if type(pressed) is not bool:
                raise ValueError('pressed must be a boolean.')
            key = payload.get('key')
            if key is not None:
                if key not in ('home', 'back', 'power', 'volumeup', 'volumedown'):
                    raise ValueError('Unknown device button.')
                if not self.capabilities['keyboard' if key == 'back' else 'buttons']:
                    raise ValueError('The device button input service is unavailable.')
                return [f'input.button {key} {int(pressed)}']
            if not self.capabilities['keyboard']:
                raise ValueError('The device keyboard service is unavailable.')
            usage = keyboard_usage(payload.get('code'))
            modifiers = _integer(payload.get('modifiers', 0), 0, 255, 'Keyboard modifiers')
            return [f'input.key {usage} {int(pressed)} {modifiers}']
        raise ValueError('Unknown screen control action.')

    def poll(self, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            if self.connection != 'diagnostic':
                return None
            if self.enabled and now - self.last_client >= self.LEASE:
                self._release()
                self.enabled = self.settings['control'] = False
                self._publish('Viewer heartbeat expired; held input released')
            if self.queue:
                return self.queue.popleft()
            if self.enabled and now >= self.next_keepalive:
                self.next_keepalive = now + 1
                return 'input.keepalive'
            return None


VIEWER_HTML_PATH = Path(__file__).with_name('debug_screen_viewer.html')


class ScreenViewer:
    def __init__(self, store, control=None):
        self.store = store
        self.control = control or ScreenControl(store)
        self.token = secrets.token_urlsafe(32)
        viewer = self
        class Handler(BaseHTTPRequestHandler):
            def _trusted_host(handler):
                return handler.headers.get('Host') == f'127.0.0.1:{handler.server.server_port}'

            def _reply(handler, status, payload, mime='application/json'):
                handler.send_response(status)
                handler.send_header('Content-Type', mime)
                handler.send_header('Content-Length', str(len(payload)))
                handler.send_header('Cache-Control', 'no-store')
                handler.send_header('X-Content-Type-Options', 'nosniff')
                handler.send_header('Referrer-Policy', 'no-referrer')
                handler.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
                handler.end_headers()
                handler.wfile.write(payload)

            def do_GET(handler):
                if not handler._trusted_host():
                    handler.send_error(403)
                    return
                path = handler.path.split('?', 1)[0]
                with store.lock:
                    if path == '/':
                        payload = VIEWER_HTML_PATH.read_bytes().replace(b'__VIEWER_TOKEN__', viewer.token.encode('ascii'))
                        mime = 'text/html; charset=utf-8'
                    elif path == '/status':
                        payload, mime = json.dumps(store.info).encode(), 'application/json'
                    elif path == '/frame.png' and store.png is not None:
                        payload, mime = store.png, 'image/png'
                    else:
                        handler.send_error(404)
                        return
                handler._reply(200, payload, mime)

            def do_POST(handler):
                if handler.path != '/control':
                    handler.send_error(404)
                    return
                origin = handler.headers.get('Origin')
                expected = f'http://127.0.0.1:{handler.server.server_port}'
                token = handler.headers.get('X-Screen-Token', '')
                if not handler._trusted_host() or (origin is not None and origin != expected) or not secrets.compare_digest(token, viewer.token):
                    handler.send_error(403)
                    return
                try:
                    length = int(handler.headers.get('Content-Length', '0'))
                    if not 0 < length <= 4096 or handler.headers.get('Transfer-Encoding'):
                        raise ValueError('Screen control payload must be 1..4096 bytes.')
                    if handler.headers.get_content_type() != 'application/json':
                        raise ValueError('Expected application/json.')
                    payload = json.loads(handler.rfile.read(length))
                    result = viewer.control.handle(payload)
                except (ValueError, UnicodeError, RecursionError) as error:
                    handler._reply(400, json.dumps({'error': str(error)}).encode())
                    return
                handler._reply(202, json.dumps(result).encode())

            def log_message(handler, *_args):
                pass
            def setup(handler):
                super().setup()
                handler.connection.settimeout(3)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}/'

    def open(self):
        webbrowser.open(self.url)

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
