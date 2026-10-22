import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('terminal', ROOT/'scripts/debug_terminal.py')
terminal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(terminal)


class Terminal(unittest.TestCase):
    def test_identity_does_not_select_unrelated_adapters(self):
        ports = [SimpleNamespace(device='COM1',vid=0x1209,pid=1,serial_number='other'),
                 SimpleNamespace(device='COM2',vid=0x1209,pid=1,serial_number='ACE5DBG001')]
        self.assertEqual(terminal.matching_ports(ports, 0x1209, 1, 'ACE5DBG001'), ['COM2'])

    def test_port_selection_requires_complete_identity(self):
        ports = [SimpleNamespace(device='COM1', vid=7, pid=8, serial_number='board')]
        self.assertEqual(terminal.matching_ports(ports), [])
        self.assertEqual(terminal.matching_ports(ports, 7, 8), [])
        self.assertEqual(terminal.matching_ports(ports, 7, 8, 'board'), ['COM1'])
        self.assertEqual(terminal.matching_ports(ports, 7, 9, 'board'), [])

    def test_polling_rejects_mutating_and_consuming_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = terminal.Capture(Path(directory))
            try:
                commands = terminal.Commands(capture, 'fake')
                for command in ('gpu.hfi.pin', 'gpu.hfi.query', 'gpu.hfi.poll',
                                'input.release', 'input.keepalive', 'wifi.start', 'reboot.fastboot'):
                    with self.assertRaises(ValueError):
                        commands.accept('watch ' + command + ' 1')
                commands.accept('watch gpu.hfi.status 1')
                self.assertEqual(commands.watch, ('gpu.hfi.status', 1.0))
            finally:
                capture.close()

    def test_commands_reject_injection(self):
        for command in ('ping\nreplay', 'x'*64, 'ls', 'reboot', 'write 0x1000 1'):
            with self.assertRaises(ValueError):
                terminal.wire_command(command)
        self.assertEqual(terminal.wire_command('ps'), b'ps\n')

    def test_hfi_diagnostic_commands(self):
        for name in ('pin', 'status', 'query', 'poll', 'log'):
            command = 'gpu.hfi.' + name
            self.assertEqual(terminal.wire_command(command), (command + '\n').encode())
            for suffix in (' now', ';ping', '\nping'):
                with self.assertRaises(ValueError):
                    terminal.wire_command(command + suffix)
        for command in ('gpu.hfi.start', 'gpu.hfi.unpin', 'gpu.hfi'):
            with self.assertRaises(ValueError):
                terminal.wire_command(command)

    def test_split_utf8_and_historical_topic_export(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = terminal.Capture(Path(directory))
            try:
                data = 'GIULIA WIFI: 测试\nGIULIA GPU: ready\n'.encode()
                a = capture.feed(data[:14])
                b = capture.feed(data[14:])
                self.assertEqual(a+b, data.decode())
                capture.save('COM2')
                self.assertEqual((capture.root/'device-000.log').read_bytes(), data)
                self.assertIn('测试', (capture.root/'wifi.txt').read_text(encoding='utf-8'))
                self.assertNotIn('GPU', (capture.root/'wifi.txt').read_text(encoding='utf-8'))
                self.assertIn('historical', (capture.root/'session.json').read_text())
            finally:
                capture.close()

    def test_split_input_status_enables_control_only_after_complete_device_record(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = terminal.Capture(Path(directory))
            try:
                control = capture.screen_control
                capture.feed(b'GIULIA INPUT: available=1 touch=1 key')
                with self.assertRaises(ValueError):
                    control.handle({'action': 'control', 'enabled': True})
                capture.feed(b'board=1 buttons=1\n')
                control.handle({'action': 'control', 'enabled': True})
                self.assertTrue(capture.screen_store.info['settings']['control'])
                capture.feed(b'GIULIA INPUT: available=0 touch=0 keyboard=0 buttons=0\n')
                self.assertFalse(capture.screen_store.info['settings']['control'])
            finally:
                capture.close()

    def test_pointer_events_use_serial_tick_without_diagnostic_command_delay(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = terminal.Capture(Path(directory))
            try:
                commands = terminal.Commands(capture, 'fake')
                writes = []
                serial = SimpleNamespace(write=lambda data: writes.append(data) or len(data))
                clock = [100.0]
                with patch.object(terminal.time, 'monotonic', side_effect=lambda: clock[0]):
                    commands.accept('ping')
                    commands.tick(serial)
                    capture.feed(b'GIULIA INPUT: available=1 touch=1 keyboard=1 buttons=1\n')
                    capture.screen_control.handle({'action': 'control', 'enabled': True})
                    capture.screen_control.handle({'action': 'touch', 'phase': 'down', 'x': 1, 'y': 2})
                    capture.screen_control.handle({'action': 'touch', 'phase': 'up', 'x': 3, 'y': 4})
                    self.assertEqual(writes, [b'ping\n'])
                    clock[0] += .02
                    commands.tick(serial)
                    clock[0] += .02
                    commands.tick(serial)
                    self.assertEqual(writes, [b'ping\n', b'input.touch down 1 2\n', b'input.touch up 3 4\n'])
                    self.assertLess(clock[0], commands.next_send)
                    capture.screen_control.handle({'action': 'key', 'code': 'KeyA', 'pressed': True})
                    clock[0] += .02
                    with self.assertRaises(OSError):
                        commands.tick(SimpleNamespace(write=lambda _data: 0))
            finally:
                capture.close()

    def test_entering_shell_drops_queued_viewer_events_before_serial_transition(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = terminal.Capture(Path(directory))
            try:
                commands = terminal.Commands(capture, 'fake')
                capture.feed(b'GIULIA INPUT: available=1 touch=1 keyboard=1 buttons=1\n')
                capture.screen_control.handle({'action': 'control', 'enabled': True})
                capture.screen_control.handle({'action': 'key', 'code': 'KeyA', 'pressed': True})
                commands.accept('shell')
                with self.assertRaises(ValueError):
                    capture.screen_control.handle({'action': 'snapshot'})
                writes = []
                serial = SimpleNamespace(write=lambda data: writes.append(data) or len(data))
                commands.tick(serial)
                self.assertEqual(writes, [b'shell\n'])
                with terminal.stop_screen_session(serial, lambda: commands.screen_started, capture.screen_control):
                    pass
                self.assertEqual(writes, [b'shell\n'])
            finally:
                capture.close()

    def test_queue_polling_and_partial_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = terminal.Capture(Path(directory))
            try:
                commands = terminal.Commands(capture, 'fake')
                with self.assertRaises(ValueError):
                    commands.accept('watch status 0')
                with self.assertRaises(ValueError):
                    commands.accept('watch replay 1')
                with self.assertRaises(ValueError):
                    commands.accept('watch wifi.start 1')
                with self.assertRaises(ValueError):
                    commands.accept('watch reboot.fastboot 1')
                commands.accept('collect')
                with self.assertRaises(ValueError):
                    commands.accept('collect')
                writes = []
                fake = SimpleNamespace(write=lambda data: writes.append(data) or len(data))
                commands.tick(fake)
                self.assertEqual(writes, [b'features\n'])
                commands.next_send = 0
                with self.assertRaises(OSError):
                    commands.tick(SimpleNamespace(write=lambda data: 0))
            finally:
                capture.close()

    def test_control_characters_never_reach_terminal(self):
        self.assertEqual(terminal.safe_text('abc\x1b\x00\x9b\n'), 'abc\n')

    def test_register_validation_and_pcie_aperture(self):
        valid=('reg.map 0x60000000 0x4000', 'reg.maps', 'reg.read 0x60000000 32',
               'reg.write 0x60000000 32 0xffffffff', 'reg.rmw 0x60000000 32 3 2',
               'reg.dump 0x60000000 32 64','reg.unmap 15','shell','shell.size 120 40','wifi.status','wifi.start')
        for cmd in valid:self.assertEqual(terminal.wire_command(cmd),(cmd+'\n').encode())
        invalid=('reg.map 0x80000000 0x4000', 'reg.map 0x60000001 0x4000',
                 'reg.map 0x60000000 0x20000','reg.read 0x60000001 32',
                 'reg.read 0x60000000 128','reg.write 0x60000000 8 256',
                 'reg.write 0x60000000 64 0x10000000000000000',
                 'reg.rmw 0x60000000 32 1 2','reg.dump 0x60000000 32 65',
                 'reg.dump 0xfffffffffffffff8 64 2','reg.unmap 16',
                 'reg.read 0x60000000 32\nshell','reg.read 0x60000000 32;reboot',
                 'shell.size 0 24','shell.size 0x80 24')
        for cmd in invalid:
            with self.subTest(cmd=cmd),self.assertRaises(ValueError):terminal.wire_command(cmd)

    def test_screen_and_input_wire_commands_validate_device_bounds(self):
        valid = ('screen.configure 160 1', 'screen.configure 2780 30',
                 'input.status', 'input.release', 'input.keepalive',
                 'input.touch down 0 65535', 'input.touch move 65535 0',
                 'input.touch up 32768 32768', 'input.touch cancel 0 0',
                 'input.key 4 1 255', 'input.key 231 0 0',
                 'input.button home 1', 'input.button home 0',
                 'input.button back 1',
                 'input.button power 1', 'input.button volumeup 0',
                 'input.button volumedown 1')
        for command in valid:
            with self.subTest(command=command):
                self.assertEqual(terminal.wire_command(command), (command + '\n').encode('ascii'))
        invalid = ('screen.configure 159 1', 'screen.configure 2781 1',
                   'screen.configure 695 0', 'screen.configure 695 31',
                   'screen.configure 695.0 1', 'screen.configure 695 1 extra',
                   'input.touch tap 0 0', 'input.touch down -1 0',
                   'input.touch up 65536 0', 'input.touch move 0 0 1',
                   'input.key 3 1 0', 'input.key 232 1 0',
                   'input.key 4 2 0', 'input.key 4 1 256',
                   'input.key 4 1 -1', 'input.button unknown 1',
                   'input.button power 2', 'input.status now',
                   'input.release\nping', 'input.keepalive now')
        for command in invalid:
            with self.subTest(command=command), self.assertRaises(ValueError):
                terminal.wire_command(command)

    def test_raw_shell_markers_split_at_every_byte(self):
        raw=b'\x1b[32mroot# \xe4\xbd\xa0\xe5\xa5\xbd\x00\xff'
        payload=b'kernel log\n'+terminal.ShellWire.BEGIN+raw+terminal.ShellWire.END+b'log again\n'
        for split in range(len(payload)+1):
            wire=terminal.ShellWire()
            events=wire.feed(payload[:split])+wire.feed(payload[split:])
            self.assertEqual(b''.join(data for kind,data in events if kind=='raw'),raw)
            self.assertEqual(b''.join(data for kind,data in events if kind=='log'),b'kernel log\nlog again\n')
            self.assertEqual([kind for kind,_ in events if kind in ('begin','end')],['begin','end'])
            self.assertFalse(wire.active)
            self.assertFalse(wire.pending)

    def test_shell_prompt_is_not_delayed_waiting_for_newline(self):
        wire=terminal.ShellWire()
        wire.feed(wire.BEGIN)
        self.assertEqual(wire.feed(b'root# '),[('raw',b'root# ')])
        self.assertEqual(wire.feed(b'\r'),[])
        self.assertEqual(wire.feed(b'X'),[('raw',b'\rX')])

    def test_reboot_requires_exact_command_and_actual_reset_ack(self):
        for command in ('reboot.fastboot','reboot.status'):
            self.assertEqual(terminal.wire_command(command),(command+'\n').encode())
        for command in ('reboot.fastboot now','reboot.fastboot\nping','reboot.fastboot;ping'):
            with self.assertRaises(ValueError):terminal.wire_command(command)
        with tempfile.TemporaryDirectory() as directory:
            capture=terminal.Capture(Path(directory))
            try:
                commands=terminal.Commands(capture,'fake')
                commands.accept('reboot.fastboot')
                commands.tick(SimpleNamespace(write=lambda data:len(data)))
                self.assertTrue(commands.reboot_sent)
                with self.assertRaises(ValueError):commands.accept('wifi.start')
                capture.feed(b'GIULIA REBOOT: accepted target=fastboot\n')
                self.assertFalse(terminal.reboot_acknowledged(capture))
                capture.feed(b'GIULIA REBOOT: resetting target=fastboot disks=shutdown-complete\n')
                self.assertTrue(terminal.reboot_acknowledged(capture))
                self.assertFalse(terminal.reboot_failed(capture))
                capture.feed(b'GIULIA REBOOT: PSCI SYSTEM_RESET returned=-1\n')
                self.assertTrue(terminal.reboot_failed(capture))
            finally:capture.close()

    def test_fastboot_wait_matches_requested_device(self):
        times=iter([0,.1,.2,.6,.7,.8])
        runner=Mock(side_effect=[SimpleNamespace(returncode=0,stdout='other\tfastboot\n'),
                                SimpleNamespace(returncode=0,stdout='wanted\tfastboot\n')])
        self.assertEqual(terminal.wait_fastboot('wanted',2,runner,lambda:next(times),lambda _:None),0)
        self.assertEqual(runner.call_count,2)
        with self.assertRaises(TimeoutError):
            terminal.wait_fastboot('wanted',1,runner,iter([0,2]).__next__,lambda _:None)

    def test_reboot_serial_flow_requires_disconnect_without_reset_failure(self):
        ack=b'GIULIA REBOOT: resetting target=fastboot disks=shutdown-complete\n'
        failure=b'GIULIA REBOOT: PSCI SYSTEM_RESET returned=-1\n'

        class Disconnected(OSError):
            pass

        class Session:
            def __init__(self, scenario):
                self.scenario=scenario
                self.incoming=[]
                self.writes=[]
                self.closed=False

            def __enter__(self):return self
            def __exit__(self,*args):self.closed=True

            @property
            def in_waiting(self):
                if self.writes and not self.incoming and self.scenario=='disconnect':
                    raise Disconnected('device left USB CDC')
                return len(self.incoming[0]) if self.incoming else 0

            def read(self,size):
                return self.incoming.pop(0) if size else b''

            def write(self,data):
                self.writes.append(data)
                self.incoming.append(ack)
                if self.scenario=='psci-return':self.incoming.append(failure)
                return len(data)

        for scenario in ('psci-return','stays-online','disconnect'):
            with self.subTest(scenario=scenario),tempfile.TemporaryDirectory() as directory:
                session=Session(scenario)
                serial_module=SimpleNamespace(Serial=Mock(return_value=session),SerialException=Disconnected)
                args=SimpleNamespace(list=False,port='COM_FAKE',command='reboot.fastboot',
                                     output=directory,seconds=1)
                clock=[0.0]
                def advance(_seconds):clock[0]+=.25
                with patch.object(terminal.time,'monotonic',side_effect=lambda:clock[0]), \
                     patch.object(terminal.time,'sleep',side_effect=advance),patch('builtins.print'):
                    if scenario=='psci-return':
                        with self.assertRaisesRegex(OSError,'Kernel reset returned'):
                            terminal.run(args,serial_module,[])
                        self.assertLess(clock[0],args.seconds)
                    elif scenario=='stays-online':
                        with self.assertRaisesRegex(TimeoutError,'reset and disconnect'):
                            terminal.run(args,serial_module,[])
                    else:
                        self.assertEqual(terminal.run(args,serial_module,[]),0)
                self.assertEqual(session.writes,[b'reboot.fastboot\n'])
                self.assertTrue(session.closed)
                captured=b''.join(p.read_bytes() for p in Path(directory).rglob('device-*.log'))
                self.assertIn(ack,captured)
                if scenario=='psci-return':self.assertIn(failure,captured)


if __name__ == '__main__':
    unittest.main()
