"""CMD USB terminal: bounded commands, raw capture, and diagnostic bundles."""
import argparse
import codecs
from collections import deque
from contextlib import contextmanager
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from debug_screen import ScreenWire, ScreenStore, ScreenViewer, ScreenControl

DEVICE_COMMANDS = ('help', 'ping', 'status', 'replay', 'sample', 'features',
                   'info', 'uptime', 'memory', 'ps', 'bootargs', 'display', 'usb', 'ufs', 'shell',
                   'wifi.start','wifi.status','reboot.fastboot','reboot.status',
                   'gpu.status','gpu.observe',
                   'gpu.hfi.pin','gpu.hfi.status','gpu.hfi.query','gpu.hfi.poll','gpu.hfi.log',
                   'screen.start','screen.stop','screen.snapshot',
                   'input.status','input.release','input.keepalive')
TOPICS = {
    'wifi': r'WIFI|PCIE|GIULIA PCI:|GIULIA SMMU:|WCN|MHI|QMI|QMP|PMU|WMI|IO80211',
    'gpu': r'GPU|GMU|ADRENO|SMMU',
    'touch': r'TOUCH|HID|TouchCom',
    'display': r'FB:|framebuffer|display|scanout|backboard',
    'ufs': r'UFS|BLOCK:|ROOT:|HFS|I/O error',
    'usb': r'USB|DEBUG:|TERM:.*usb',
    'process': r'SMP |pid=|launchd|SpringBoard|backboard',
    'panic': r'panic|fault|exception|crash|abort',
    'power': r'power|clock|GDSC|regulator|PMIC|battery',
    'all': r'.',
}
HELP = '''Device commands (new kernel needed except help/ping/status/replay/sample):
  info uptime memory ps bootargs display usb ufs features
  help / ping / status / replay / sample (GUI sampler)
  wifi.status / wifi.start   inspect/release an opted-in pre-DMA wait
  gpu.status              retained GPU preparation/last-observation state
  gpu.observe             queue gated read-only power/SMMU observation
  gpu.hfi.pin             retain diagnostic DMA buffers until reboot (mode 3)
  gpu.hfi.status          inspect the 17 HWSCHED queue headers
  gpu.hfi.query           enqueue warmboot query; manual doorbell still required
  gpu.hfi.poll            drain bounded HFI reply/debug packets
  gpu.hfi.log             read the first 64 words of the GMU log buffer
  reboot.fastboot         sync disks and restart into Fastboot (debug kernel)
  reboot.status           inspect a pending reboot request
  screen.start            live screen with mouse/keyboard controls in browser
  screen.stop             stop screen transfer (logs and commands continue)
  screen.snapshot         save a real framebuffer screenshot as PNG
  screen.configure N FPS  maximum edge 160..2780, target FPS 1..30 (USB limited)
  input.status            actual touch/keyboard/button service availability
  input.release           release remote touches and held keyboard/buttons
Host commands:
  :help                  this help
  logs TOPIC             retained session logs, NOT fresh hardware queries
                         wifi gpu touch display ufs usb process panic power all
  all                    queue all bounded device queries
  collect                all queries + retained RAM replay + GUI sample;
                         saves a diagnostic bundle after 15 seconds
  save                   save current session metadata and topic logs
  watch COMMAND SECONDS  periodically query (minimum 1 second)
  unwatch                stop polling
  clear                  clear screen (keep logs)
  exit / quit / :quit    close port
  shell.size COLS ROWS    set PTY dimensions before entering shell
  shell                  real PTY shell (debug kernel + staged daemon/shell)
                         Ctrl+C goes to phone; Ctrl+] leaves shell
  reg.map BASE BYTES      map explicit peripheral window (no device access)
  reg.maps / reg.unmap N  list / release mapped window
  reg.read ADDR WIDTH     one actual MMIO read (WIDTH: 8/16/32/64)
  reg.write ADDR WIDTH V  one actual MMIO write, no automatic readback
  reg.rmw ADDR WIDTH M V  read/modify/write with mask M, bits V (not atomic)
  reg.dump ADDR WIDTH N   read at most 64 consecutive registers
MMIO requires giulia_debug=1 giulia_mmio=1; operator manages clocks/power.
Up/Down: command history. Ctrl+C exits only outside shell.
'''


def wire_command(line):
    words = line.split()
    register_arity = {'reg.map': 2, 'reg.maps': 0, 'reg.unmap': 1,
                      'reg.read': 2, 'reg.write': 3, 'reg.rmw': 4, 'reg.dump': 3,
                      'shell.size': 2}
    if words and words[0] in ('screen.configure', 'input.touch', 'input.key', 'input.button'):
        command = words[0]
        if command == 'input.button':
            valid = len(words) == 3 and words[1] in ('home','back','power','volumeup','volumedown') and words[2] in ('0','1')
        else:
            start = 2 if command == 'input.touch' else 1
            numbers = words[start:]
            valid = len(words) == {'screen.configure':3, 'input.touch':4, 'input.key':4}[command]
            valid = valid and all(re.fullmatch(r'[0-9]{1,5}', n) for n in numbers)
            if valid:
                values = [int(n) for n in numbers]
                if command == 'screen.configure':
                    valid = 160 <= values[0] <= 2780 and 1 <= values[1] <= 30
                elif command == 'input.touch':
                    valid = words[1] in ('down','move','up','cancel') and all(0 <= n <= 65535 for n in values)
                else:
                    valid = 4 <= values[0] <= 231 and values[1] in (0,1) and 0 <= values[2] <= 255
        if not valid:
            raise ValueError('Invalid screen/input command; use :help.')
    elif words and words[0] == 'gpu.dev':
        if len(words)!=7 or any(not re.fullmatch(r'(?:0x[0-9a-f]+|[0-9]+)', x) for x in words[1:]):
            raise ValueError('Invalid GPU development command')
        if any(int(x,16 if x.startswith('0x') else 10)>0xffffffff for x in words[1:]):
            raise ValueError('GPU development argument overflow')
    elif words and words[0] in register_arity:
        if (len(words) != register_arity[words[0]] + 1 or
                any(not re.fullmatch(r'(?:0[xX][0-9a-fA-F]+|[0-9]+)', x) for x in words[1:])):
            raise ValueError('Invalid register syntax; use :help.')
        if any(int(x, 16 if x.lower().startswith('0x') else 10) > (1 << 64)-1 for x in words[1:]):
            raise ValueError('Register argument exceeds 64 bits.')
        values = [int(x,16 if x.lower().startswith('0x') else 10) for x in words[1:]]
        command = words[0]
        if command == 'shell.size':
            if any(not x.isdecimal() for x in words[1:]) or any(not 1 <= x <= 1000 for x in values):
                raise ValueError('Shell size requires decimal columns/rows in 1..1000.')
        elif command in ('reg.read','reg.write','reg.rmw','reg.dump'):
            address,width = values[:2]
            if width not in (8,16,32,64) or address % (width//8):
                raise ValueError('Width must be 8/16/32/64 and address naturally aligned.')
            if command in ('reg.write','reg.rmw') and any(x >= 1 << width for x in values[2:]):
                raise ValueError('Value/mask exceeds selected register width.')
            if command == 'reg.rmw' and values[3] & ~values[2]:
                raise ValueError('RMW bits must be contained in the mask.')
            if command == 'reg.dump' and (not 1 <= values[2] <= 64 or address+(values[2]-1)*(width//8) >= 1 << 64):
                raise ValueError('Dump length must be 1..64 without address overflow.')
        elif command == 'reg.map':
            address,size = values
            if not 0x100000 <= address < 0x80000000 or not 0 < size <= 0x10000 or address+size > 0x80000000:
                raise ValueError('Map must fit the low peripheral aperture, maximum 64 KiB.')
            if address % 4096 or size % 4096:
                raise ValueError('Map must be page aligned; the kernel enforces its actual page size.')
        elif command == 'reg.unmap' and values[0] >= 16:
            raise ValueError('Mapping slot must be 0..15.')
    elif line not in DEVICE_COMMANDS:
        raise ValueError('Unknown diagnostic command; use :help, or enter shell for userspace commands.')
    if len(line) > 63 or any(ord(c)<32 or ord(c)>126 for c in line):
        raise ValueError('Kernel command limit is 63 printable ASCII bytes.')
    return (line + '\n').encode('ascii')


class ShellWire:
    """Incremental raw-mode markers, including every possible USB split."""
    BEGIN = b'\r\nGIULIA SHELL BEGIN\r\n'
    END = b'\r\nGIULIA SHELL END\r\n'

    def __init__(self):
        self.active = False
        self.pending = b''

    def feed(self, data):
        self.pending += data
        events = []
        while self.pending:
            marker = self.END if self.active else self.BEGIN
            at = self.pending.find(marker)
            if at >= 0:
                if at:
                    events.append(('raw' if self.active else 'log', self.pending[:at]))
                self.pending = self.pending[at+len(marker):]
                self.active = not self.active
                events.append(('begin' if self.active else 'end', b''))
                continue
            keep = 0
            for length in range(1, min(len(marker), len(self.pending)+1)):
                if self.pending.endswith(marker[:length]):
                    keep = length
            ready = self.pending[:-keep] if keep else self.pending
            self.pending = self.pending[-keep:] if keep else b''
            if ready:
                events.append(('raw' if self.active else 'log', ready))
            break
        return events


class WindowsConsole:
    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.k = ctypes.WinDLL('kernel32', use_last_error=True)
        self.k.GetStdHandle.argtypes = [wintypes.DWORD]
        self.k.GetStdHandle.restype = wintypes.HANDLE
        self.k.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        self.k.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.handles = [self.k.GetStdHandle(-10 & 0xffffffff), self.k.GetStdHandle(-11 & 0xffffffff)]
        self.modes = []
        for h in self.handles:
            mode = wintypes.DWORD()
            if not self.k.GetConsoleMode(h, ctypes.byref(mode)):
                raise OSError('Raw shell requires Windows console input/output.')
            self.modes.append(mode.value)

    def raw(self, enabled):
        if enabled:
            if not self.k.SetConsoleMode(self.handles[0], self.modes[0] & ~7):
                raise OSError('Cannot enable raw keyboard mode.')
            if not self.k.SetConsoleMode(self.handles[1], self.modes[1] | 4):
                self.restore()
                raise OSError('Cannot enable VT terminal output.')
        else:
            self.restore()

    def restore(self):
        for handle, mode in zip(self.handles, self.modes):
            self.k.SetConsoleMode(handle, mode)


def safe_text(text):
    return ''.join(c for c in text if c in '\n\r\t' or (ord(c) >= 32 and not 127 <= ord(c) <= 159))


def matching_ports(ports, vid=None, pid=None, serial_number=None):
    # Never guess a device from a generic CDC adapter or a partial identity.
    if vid is None or pid is None or not serial_number:
        return []
    return [p.device for p in ports if p.vid == vid and p.pid == pid
            and p.serial_number == serial_number]


class Capture:
    def __init__(self, root):
        root.mkdir(parents=True, exist_ok=True)
        self.root = root / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        self.root.mkdir()
        self.part = 0
        self.stream = (self.root / 'device-000.log').open('xb')
        self.decoder = codecs.getincrementaldecoder('utf-8')('replace')
        self.lines = deque(maxlen=20000)
        self.pending = ''
        self.events = []
        self.total = 0
        self.screen_wire = ScreenWire()
        self.screen_store = ScreenStore(self.root / 'screens')
        self.screen_control = ScreenControl(self.screen_store)
        self.viewer = None
        self.last_text = b''
        self.screen_notices = deque()

    def feed(self, data):
        incoming = len(data)
        data, frames = self.screen_wire.feed(data)
        self.last_text = data
        for frame in frames:
            path = self.screen_store.receive(frame)
            if frame[1] or self.screen_store.info['frames'] == 1:
                self.screen_notices.append('Screen PNG: ' + str(path.resolve()))
        if self.screen_wire.last_event == 'stop':
            self.screen_store.set_state('screen transfer stopped; last frame retained')
        if self.stream.tell() + len(data) > 32 * 1024 * 1024:
            self.stream.close()
            self.part += 1
            self.stream = (self.root / f'device-{self.part:03}.log').open('xb')
        self.stream.write(data)
        self.stream.flush()
        self.total += incoming
        text = self.decoder.decode(data)
        chunks = (self.pending + text).split('\n')
        self.lines.extend(chunks[:-1])
        for record in chunks[:-1]:
            self.screen_control.observe(record.rstrip('\r'))
        self.pending = chunks[-1]
        # Bound an unterminated line from a noisy device.
        if len(self.pending) > 16384:
            self.lines.append(self.pending[:16384])
            self.pending = self.pending[-16384:]
        return safe_text(text)

    def filtered(self, topic):
        if topic not in TOPICS:
            raise ValueError('Topics: ' + ' '.join(TOPICS))
        return [line for line in [*self.lines, self.pending] if re.search(TOPICS[topic], line, re.I)]

    def save(self, port):
        for topic in TOPICS:
            (self.root / f'{topic}.txt').write_text('\n'.join(self.filtered(topic)), encoding='utf-8')
        (self.root / 'session.json').write_text(json.dumps({
            'port': port, 'bytes': self.total, 'commands': self.events,
            'topic_source': 'last 20000 session log lines; historical, not live snapshots',
            'raw_logs': self.part + 1,
            'screen_binary_separated': True,
            'screen_frames': self.screen_store.info['frames'],
            'screen_decode_errors': self.screen_wire.errors,
        }, indent=2), encoding='utf-8')
        return self.root

    def close(self):
        self.screen_control.set_connection('disconnected')
        self.stream.close()
        if self.viewer:
            self.viewer.close()

    def preview(self):
        if self.viewer is None:
            self.viewer = ScreenViewer(self.screen_store, self.screen_control)
            self.viewer.open()
        return self.viewer.url


class Commands:
    def __init__(self, capture, port):
        self.capture, self.port = capture, port
        self.queue = deque()
        self.watch = None
        self.next_watch = 0
        self.next_send = 0
        self.save_at = None
        self.shell_deadline = None
        self.reboot_sent = False
        self.screen_started = False
        self.next_control = 0

    def accept(self, line):
        words = line.strip().split()
        if not words:
            return ''
        cmd = words[0]
        if cmd in ('exit', 'quit', ':quit'):
            return None
        if cmd == ':help':
            return HELP
        if cmd == 'logs' and len(words) == 2:
            return '[HISTORICAL SESSION LOGS]\n' + ('\n'.join(self.capture.filtered(words[1])) or 'No matching records captured.')
        if cmd == 'save':
            return 'Saved: ' + str(self.capture.save(self.port))
        if cmd == 'unwatch':
            self.watch = None
            return 'Polling stopped.'
        if cmd == 'watch' and len(words) == 3:
            wire_command(words[1])
            if words[1] not in ('ping', 'status', 'features', 'info', 'uptime', 'memory',
                                 'ps', 'bootargs', 'display', 'usb', 'ufs', 'wifi.status',
                                 'gpu.status', 'gpu.hfi.status', 'reboot.status', 'input.status'):
                raise ValueError('Only read-only status queries support periodic polling.')
            seconds = float(words[2])
            if not 1 <= seconds <= 86400:
                raise ValueError('Polling interval must be 1..86400 seconds.')
            self.watch = (words[1], seconds)
            self.next_watch = 0
            return 'Polling enabled.'
        if cmd in ('all', 'collect') and len(words) == 1:
            if self.queue or self.save_at is not None:
                raise ValueError('A collection is already pending.')
            self.watch = None
            self.queue.extend(('features','info','uptime','memory','ps','bootargs','display','usb','ufs','gpu.status','status'))
            if cmd == 'collect':
                self.queue.extend(('replay','sample'))
                self.save_at = time.monotonic() + 15
            return 'Queries queued; old kernels will report unsupported commands.'
        if len(self.queue) >= 32:
            raise ValueError('Command queue full; wait for pending queries.')
        wire_command(line)
        if self.reboot_sent:
            raise ValueError('Reboot already sent; wait for Fastboot.')
        if line == 'reboot.fastboot':
            if self.queue or self.save_at is not None or self.shell_deadline is not None:
                raise ValueError('Wait for pending commands before rebooting.')
            self.watch = None
            self.capture.screen_control.set_connection('reboot')
        if line == 'shell':
            if self.queue or self.save_at is not None or self.shell_deadline is not None:
                raise ValueError('Wait for pending commands before entering shell.')
            self.watch = None
            self.capture.screen_control.set_connection('shell')
        self.queue.append(line)
        if line == 'screen.start':
            return 'Live screen viewer: ' + self.capture.preview()
        return ''

    def tick(self, serial):
        now = time.monotonic()
        if self.watch and now >= self.next_watch and not self.queue:
            self.queue.append(self.watch[0])
            self.next_watch = now + self.watch[1]
        if self.queue and now >= self.next_send:
            command = self.queue.popleft()
            data = wire_command(command)
            if serial.write(data) != len(data):
                raise OSError('Incomplete command write; reconnect before retrying.')
            self.capture.events.append({'time': datetime.now().isoformat(), 'sent': command})
            if command == 'shell':
                self.shell_deadline = now + 5
                self.screen_started = False
            if command == 'screen.start':
                self.screen_started = True
                self.capture.screen_control.request_status()
            if command == 'screen.stop':
                self.screen_started = False
                self.capture.screen_control.handle({'action': 'control', 'enabled': False})
            if command == 'reboot.fastboot':
                self.reboot_sent = True
            self.next_send = now + 0.4
        elif now >= self.next_control:
            command = self.capture.screen_control.poll(now)
            if command:
                data = wire_command(command)
                if serial.write(data) != len(data):
                    raise OSError('Incomplete screen control write; reconnect before retrying.')
                # Movement is transient; retaining every pointer/heartbeat would
                # grow session metadata for the entire duration of mirroring.
                if not command.startswith('input.'):
                    self.capture.events.append({'time': datetime.now().isoformat(), 'sent': command})
                if command == 'screen.start':
                    self.screen_started = True
                elif command == 'screen.stop':
                    self.screen_started = False
                self.next_control = now + 0.01
        if self.save_at is not None and now >= self.save_at and not self.queue:
            self.save_at = None
            return 'Saved: ' + str(self.capture.save(self.port))
        return ''


def reboot_acknowledged(capture):
    return any('GIULIA REBOOT: resetting target=fastboot disks=shutdown-complete' in line
               for line in [*capture.lines, capture.pending])


def reboot_failed(capture):
    return any('GIULIA REBOOT: PSCI SYSTEM_RESET returned=' in line or
               'GIULIA REBOOT: shutdown returned=' in line
               for line in [*capture.lines, capture.pending])


def wait_fastboot(serial_number, timeout, runner=subprocess.run,
                  now=time.monotonic, sleep=time.sleep):
    deadline = now() + timeout
    while now() < deadline:
        try:
            result = runner(['fastboot', 'devices'], capture_output=True, text=True,
                            timeout=min(3, max(.1, deadline-now())), check=False)
            if result.returncode == 0 and any(
                    line.split() == [serial_number, 'fastboot'] for line in result.stdout.splitlines()):
                print('Fastboot verified for the requested device.', flush=True)
                return 0
        except subprocess.TimeoutExpired:
            pass
        sleep(min(.5, max(0, deadline-now())))
    raise TimeoutError('Requested device did not appear in Fastboot before the timeout.')


@contextmanager
def stop_screen_session(serial, active, control=None):
    try:
        yield
    finally:
        if control:
            # This runs before closing the sole serial connection. The kernel
            # also releases input on DTR loss and its independent lease timeout.
            try:
                if control.available and control.connection == 'diagnostic':
                    serial.write(wire_command('input.release'))
            except OSError:
                pass
            control.set_connection('disconnected')
        if active():
            try:
                serial.write(wire_command('screen.stop'))
            except OSError:
                pass  # Disconnect also stops the kernel producer.


def run(args, serial_module, ports):
    if args.list:
        for p in ports:
            print(f'{p.device}: {p.description} [{p.hwid}]')
        return 0
    found = matching_ports(ports, getattr(args, 'vid', None),
                           getattr(args, 'pid', None), getattr(args, 'usb_serial', None))
    port = args.port or (found[0] if len(found) == 1 else None)
    if not port:
        raise ValueError('No unique CDC port selected. Use --list and --port, or specify --vid, --pid and --usb-serial.')
    if not args.command and (os.name != 'nt' or not sys.stdin.isatty()):
        raise ValueError('Interactive mode requires Windows CMD; use --command for scripted capture.')
    capture = Capture(Path(args.output).resolve())
    console = None
    reboot_disconnected = False
    commands = None
    try:
        # pySerial defaults to DTR/RTS asserted; CDC transmits only while DTR is set.
        with serial_module.Serial(port, 115200, timeout=0, write_timeout=2) as serial, \
                stop_screen_session(serial, lambda: commands is not None and commands.screen_started, capture.screen_control):
            commands = Commands(capture, port)
            print(f'Connected {port}. Logs: {capture.root}\n' + HELP)
            line = ''
            history = []
            history_index = 0
            def show(text):
                if not text:
                    return
                text = safe_text(text)
                if not args.command:
                    print('\r' + ' ' * (len(line) + 8) + '\r', end='')
                print(text, end='' if text.endswith('\n') else '\n', flush=True)
                if not args.command:
                    print('unixnu> ' + line, end='', flush=True)
            if args.command:
                if getattr(args, 'max_size', None) is not None or getattr(args, 'max_fps', None) is not None:
                    show(commands.accept(f'screen.configure {args.max_size or 695} {args.max_fps or 1}'))
                show(commands.accept(args.command))
            else:
                import msvcrt
                print('unixnu> ', end='', flush=True)
            end = time.monotonic() + args.seconds
            extended = False
            wire = ShellWire()
            log_decoder = codecs.getincrementaldecoder('utf-8')('replace')
            if not args.command:
                console = WindowsConsole()
            while not args.command or time.monotonic() < end:
                try:
                    data = serial.read(min(serial.in_waiting, 16384))
                except (OSError, serial_module.SerialException):
                    if not commands.reboot_sent or not reboot_acknowledged(capture) or reboot_failed(capture):
                        raise
                    reboot_disconnected = True
                    show('USB disconnected after the kernel completed shutdown for Fastboot.')
                    break
                if data:
                    capture.feed(data)
                    if commands.reboot_sent and reboot_failed(capture):
                        raise OSError('Kernel reset returned without rebooting; inspect the saved log.')
                    while capture.screen_notices:
                        show(capture.screen_notices.popleft())
                    for kind, chunk in wire.feed(capture.last_text):
                        if kind == 'log':
                            show(safe_text(log_decoder.decode(chunk)))
                        elif kind == 'begin':
                            commands.shell_deadline = None
                            capture.screen_control.set_connection('shell')
                            if console:
                                console.raw(True)
                            print('\r\n[Phone PTY: Ctrl+] returns to debugger]\r', flush=True)
                        elif kind == 'raw':
                            sys.stdout.buffer.write(chunk)
                            sys.stdout.buffer.flush()
                        else:
                            capture.screen_control.set_connection('diagnostic')
                            capture.screen_control.request_status()
                            if console:
                                console.raw(False)
                            print('\r\n[Shell ended]', flush=True)
                            if not args.command:
                                print('unixnu> ', end='', flush=True)
                if not wire.active:
                    show(commands.tick(serial))
                    if commands.shell_deadline and time.monotonic() >= commands.shell_deadline:
                        commands.shell_deadline = None
                        capture.screen_control.set_connection('diagnostic')
                        show('Shell did not start. Check giulia_debug=1 and the installed daemon/shell.')
                if not args.command and msvcrt.kbhit():
                    key = msvcrt.getwch()
                    if wire.active:
                        if key in ('\x00', '\xe0'):
                            extended = True
                            continue
                        if extended:
                            extended = False
                            encoded = {'H':b'\x1b[A','P':b'\x1b[B','M':b'\x1b[C','K':b'\x1b[D',
                                       'G':b'\x1b[H','O':b'\x1b[F','S':b'\x1b[3~',
                                       'I':b'\x1b[5~','Q':b'\x1b[6~'}.get(key,b'')
                        else:
                            encoded = key.encode('utf-8', errors='replace')
                        if encoded and serial.write(encoded) != len(encoded):
                            raise OSError('Incomplete shell input write.')
                        continue
                    if commands.shell_deadline:
                        # Do not accidentally interpret shell input as a kernel command.
                        if key == '\x03':
                            serial.write(b'\x1d')
                            break
                        continue
                    if key in ('\x00', '\xe0'):
                        extended = True
                        continue
                    if extended:
                        extended = False
                        if key in ('H', 'P'):
                            history_index = max(0, min(len(history), history_index + (-1 if key == 'H' else 1)))
                            previous = len(line)
                            line = history[history_index] if history_index < len(history) else ''
                            print('\r' + ' ' * (previous + 6) + '\runixnu> ' + line, end='', flush=True)
                        continue
                    if key == '\x03':
                        break
                    if key == '\r':
                        print()
                        command, line = line.strip(), ''
                        if command:
                            history.append(command)
                            history = history[-100:]
                            history_index = len(history)
                        if command == 'clear':
                            os.system('cls')
                            show('Screen cleared; logs retained.')
                        else:
                            try:
                                reply = commands.accept(command)
                                if reply is None:
                                    break
                                show((reply or 'Queued.') if command else '')
                            except ValueError as error:
                                show(str(error))
                        if not command:
                            print('unixnu> ', end='', flush=True)
                    elif key == '\b' and line:
                        line = line[:-1]
                        print('\b \b', end='', flush=True)
                    elif 32 <= ord(key) <= 126 and len(line) < 120:
                        line += key
                        print(key, end='', flush=True)
                time.sleep(0.01)
            if args.command == 'reboot.fastboot' and (
                    not reboot_acknowledged(capture) or reboot_failed(capture) or not reboot_disconnected):
                raise TimeoutError('Kernel did not complete the Fastboot reset and disconnect; inspect the saved log.')
    finally:
        if console:
            console.restore()
        try:
            capture.save(port)
        finally:
            capture.close()
        print(f'\nSaved session: {capture.root}')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', help='Explicit serial port, e.g. COM21 or /dev/ttyACM0')
    parser.add_argument('--vid', type=lambda value: int(value, 0), help='USB vendor ID, e.g. 0x1209')
    parser.add_argument('--pid', type=lambda value: int(value, 0), help='USB product ID, e.g. 0x0001')
    parser.add_argument('--usb-serial', help='Exact USB serial number for automatic selection')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--command', help='One command, or collect/all')
    parser.add_argument('--seconds', type=float, default=20)
    parser.add_argument('--fastboot-serial', help='For reboot.fastboot: wait for this exact Fastboot device before success')
    parser.add_argument('--output', default=str(Path(__file__).resolve().parent / '../out/terminal'))
    parser.add_argument('-m', '--max-size', type=int, help='Maximum mirrored edge, 160..2780; keeps panel aspect ratio')
    parser.add_argument('--max-fps', type=int, help='Target capture rate, 1..30; actual rate depends on USB bandwidth')
    args = parser.parse_args()
    identity = (args.vid, args.pid, args.usb_serial)
    if any(value is not None for value in identity):
        if any(value is None for value in identity) or not args.usb_serial:
            parser.error('--vid, --pid and --usb-serial must be supplied together')
        if not 0 <= args.vid <= 65535 or not 0 <= args.pid <= 65535:
            parser.error('USB vendor/product IDs must be 0..65535')
    if not 1 <= args.seconds <= 86400:
        parser.error('--seconds must be 1..86400')
    if args.max_size is not None and not 160 <= args.max_size <= 2780:
        parser.error('--max-size must be 160..2780')
    if args.max_fps is not None and not 1 <= args.max_fps <= 30:
        parser.error('--max-fps must be 1..30')
    if (args.max_size is not None or args.max_fps is not None) and args.command not in ('screen.start','screen.snapshot'):
        parser.error('--max-size/--max-fps require --command screen.start or screen.snapshot')
    if args.command == 'shell':
        parser.error('Use interactive mode for shell; --command cannot control a PTY.')
    if args.fastboot_serial:
        if args.command != 'reboot.fastboot':
            parser.error('--fastboot-serial requires --command reboot.fastboot')
        if not shutil.which('fastboot'):
            parser.error('fastboot must be on PATH to verify the reboot')
    try:
        import serial
        from serial.tools import list_ports
    except ImportError:
        print('Install dependency in CMD: python -m pip install pyserial==3.5', file=sys.stderr)
        return 2
    try:
        result = run(args, serial, list(list_ports.comports()))
        if not result and args.fastboot_serial:
            return wait_fastboot(args.fastboot_serial, args.seconds)
        return result
    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError, serial.SerialException) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
