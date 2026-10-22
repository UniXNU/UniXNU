"""Desktop input reaches the serialized USB writer only through bounded actions."""
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

urlopen = build_opener(ProxyHandler({})).open

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import debug_screen as screen


@contextmanager
def control_session():
    with tempfile.TemporaryDirectory() as directory:
        store = screen.ScreenStore(Path(directory) / 'screens')
        control = screen.ScreenControl(store)
        try:
            yield store, control
        finally:
            control.shutdown()


def ready(control):
    control.set_connection('diagnostic')
    control.observe('GIULIA INPUT: available=1 touch=1 keyboard=1 buttons=1')


def drain(control, count=256):
    result = []
    for _ in range(count):
        command = control.poll()
        if command is None:
            return result
        result.append(command)
    raise AssertionError('Input queue did not drain within its bound')


class ScreenControl(unittest.TestCase):
    def test_configuration_is_queued_and_bounded_without_claiming_a_new_frame(self):
        with control_session() as (store, control):
            control.handle({'action': 'configure', 'max_size': 1280, 'max_fps': 10})
            self.assertIn('screen.configure 1280 10', drain(control))
            self.assertEqual(store.info['frames'], 0)
            for payload in ({'action': 'configure', 'max_size': 2781, 'max_fps': 1},
                            {'action': 'configure', 'max_size': 160, 'max_fps': 31},
                            {'action': 'configure', 'max_size': True, 'max_fps': 1},
                            {'action': 'command', 'command': 'reboot.fastboot'},
                            {'action': 'configure', 'max_size': '695\nreboot.fastboot', 'max_fps': 1}):
                with self.subTest(payload=payload), self.assertRaises(ValueError):
                    control.handle(payload)
            self.assertFalse(drain(control))

    def test_input_requires_explicit_control_and_real_device_capability(self):
        with control_session() as (_, control):
            touch = {'action': 'touch', 'phase': 'down', 'x': 0, 'y': 65535}
            with self.assertRaises(ValueError):
                control.handle(touch)
            ready(control)
            with self.assertRaises(ValueError):
                control.handle(touch)
            control.handle({'action': 'control', 'enabled': True})
            drain(control)
            control.handle(touch)
            self.assertIn('input.touch down 0 65535', drain(control))
            control.handle({'action': 'control', 'enabled': False})
            with self.assertRaises(ValueError):
                control.handle(touch)
            self.assertIn('input.release', drain(control))

    def test_keyboard_and_button_mapping_uses_hid_without_command_injection(self):
        with control_session() as (_, control):
            ready(control)
            control.handle({'action': 'control', 'enabled': True})
            drain(control)
            control.handle({'action': 'key', 'code': 'KeyA', 'pressed': True, 'modifiers': 2})
            control.handle({'action': 'key', 'code': 'KeyA', 'pressed': False, 'modifiers': 0})
            control.handle({'action': 'key', 'key': 'home', 'pressed': True})
            control.handle({'action': 'key', 'key': 'home', 'pressed': False})
            commands = drain(control)
            self.assertEqual(commands, ['input.key 4 1 2', 'input.key 4 0 0',
                                        'input.button home 1', 'input.button home 0'])
            for payload in ({'action': 'key', 'code': 'KeyA\nreboot.fastboot', 'pressed': True},
                            {'action': 'key', 'code': 'KeyA', 'pressed': 1},
                            {'action': 'key', 'code': 'KeyA', 'pressed': True, 'modifiers': 256},
                            {'action': 'touch', 'phase': 'down', 'x': -1, 'y': 0},
                            {'action': 'touch', 'phase': 'down', 'x': 0, 'y': 65536}):
                with self.subTest(payload=payload), self.assertRaises(ValueError):
                    control.handle(payload)

    def test_shell_and_disconnect_drop_pending_input_and_reject_new_actions(self):
        for connection in ('shell', 'reboot', 'disconnected'):
            with self.subTest(connection=connection), control_session() as (_, control):
                ready(control)
                control.handle({'action': 'control', 'enabled': True})
                drain(control)
                control.handle({'action': 'key', 'code': 'KeyA', 'pressed': True})
                control.set_connection(connection)
                self.assertNotIn('input.key 4 1 0', drain(control))
                with self.assertRaises(ValueError):
                    control.handle({'action': 'touch', 'phase': 'down', 'x': 0, 'y': 0})
                with self.assertRaises(ValueError):
                    control.handle({'action': 'start'})

    def test_capabilities_are_checked_individually_and_preserved_after_frames(self):
        with control_session() as (store, control):
            control.observe('GIULIA INPUT: available=1 touch=1 keyboard=0 buttons=0')
            control.handle({'action': 'control', 'enabled': True})
            drain(control)
            for payload in ({'action': 'key', 'code': 'KeyA', 'pressed': True},
                            {'action': 'key', 'key': 'home', 'pressed': True},
                            {'action': 'key', 'key': 'back', 'pressed': True}):
                with self.subTest(payload=payload), self.assertRaises(ValueError):
                    control.handle(payload)
            control.handle({'action': 'touch', 'phase': 'down', 'x': 10, 'y': 20})
            store.receive((3, 0, 1, 1, b'\0\xf8'))
            self.assertTrue(store.info['input_available'])
            self.assertEqual(store.info['input_capabilities'],
                             {'touch': True, 'keyboard': False, 'buttons': False})
            self.assertTrue(store.info['settings']['control'])
            self.assertEqual(store.info['connection'], 'diagnostic')
            self.assertIn('input.touch down 10 20', drain(control))

    def test_lost_viewer_heartbeat_releases_held_input_and_requires_opt_in_again(self):
        with control_session() as (store, control), patch.object(screen.time, 'monotonic', return_value=100) as now:
            ready(control)
            control.handle({'action': 'control', 'enabled': True})
            control.handle({'action': 'touch', 'phase': 'down', 'x': 10, 'y': 20})
            self.assertEqual(control.poll(100), 'input.touch down 10 20')
            self.assertEqual(control.poll(100), 'input.keepalive')
            now.return_value = 102
            control.handle({'action': 'heartbeat'})
            self.assertEqual(control.poll(103), 'input.keepalive')
            self.assertTrue(store.info['settings']['control'])
            self.assertEqual(control.poll(104.6), 'input.release')
            self.assertFalse(store.info['settings']['control'])
            self.assertIsNone(control.poll(105))
            with self.assertRaises(ValueError):
                control.handle({'action': 'key', 'code': 'KeyA', 'pressed': True})

    def test_drag_coalesces_moves_but_preserves_contact_boundaries(self):
        with control_session() as (_, control):
            ready(control)
            control.handle({'action': 'control', 'enabled': True})
            drain(control)
            control.handle({'action': 'touch', 'phase': 'down', 'x': 10, 'y': 20})
            for x in range(11, 101):
                control.handle({'action': 'touch', 'phase': 'move', 'x': x, 'y': 20})
            control.handle({'action': 'touch', 'phase': 'up', 'x': 100, 'y': 20})
            self.assertEqual(drain(control), ['input.touch down 10 20', 'input.touch move 100 20',
                                             'input.touch up 100 20'])

    def test_overflow_discards_pending_input_and_releases_instead_of_sticking_keys(self):
        with control_session() as (store, control):
            ready(control)
            control.handle({'action': 'control', 'enabled': True})
            drain(control)
            for index in range(control.LIMIT):
                control.handle({'action': 'key', 'code': 'KeyA', 'pressed': index % 2 == 0})
            with self.assertRaises(ValueError):
                control.handle({'action': 'key', 'code': 'KeyA', 'pressed': False})
            self.assertFalse(store.info['settings']['control'])
            self.assertEqual(drain(control), ['input.release'])

    def test_full_queue_still_accepts_a_replacement_for_its_last_pointer_move(self):
        with control_session() as (store, control):
            ready(control)
            control.handle({'action': 'control', 'enabled': True})
            drain(control)
            for index in range(control.LIMIT - 2):
                control.handle({'action': 'key', 'code': 'KeyA', 'pressed': index % 2 == 0})
            control.handle({'action': 'touch', 'phase': 'down', 'x': 10, 'y': 20})
            control.handle({'action': 'touch', 'phase': 'move', 'x': 30, 'y': 40})
            control.handle({'action': 'touch', 'phase': 'move', 'x': 50, 'y': 60})
            commands = drain(control)
            self.assertEqual(len(commands), control.LIMIT)
            self.assertEqual(commands[-2:], ['input.touch down 10 20', 'input.touch move 50 60'])
            self.assertTrue(store.info['settings']['control'])

    def test_scroll_produces_one_bounded_gesture_and_rejects_nonfinite_deltas(self):
        with control_session() as (_, control):
            ready(control)
            control.handle({'action': 'control', 'enabled': True})
            drain(control)
            control.handle({'action': 'scroll', 'x': 32000, 'y': 32000,
                            'delta_x': 0, 'delta_y': 100})
            commands = drain(control)
            self.assertTrue(commands[0].startswith('input.touch down '))
            self.assertTrue(commands[-1].startswith('input.touch up '))
            self.assertLessEqual(len(commands), 16)
            end_x, end_y = map(int, commands[-1].split()[-2:])
            self.assertEqual(end_x, 32000)
            self.assertLess(end_y, 32000)
            for delta in (float('inf'), float('nan'), True, 10001):
                with self.subTest(delta=delta), self.assertRaises(ValueError):
                    control.handle({'action': 'scroll', 'x': 32000, 'y': 32000, 'delta_y': delta})

    def test_viewer_authorizes_bounded_actions_and_never_writes_serial_in_http(self):
        with control_session() as (store, control):
            viewer = screen.ScreenViewer(store, control)
            try:
                def post(payload, headers=None):
                    headers = headers or {}
                    request = Request(viewer.url + 'control', data=json.dumps(payload).encode(),
                                      headers={'Content-Type': 'application/json', **headers})
                    return urlopen(request)

                for headers in ({}, {'X-Screen-Token': 'wrong'},
                                {'X-Screen-Token': viewer.token, 'Origin': 'https://unrelated.example'},
                                {'X-Screen-Token': viewer.token, 'Host': 'unrelated.example'}):
                    with self.subTest(headers=headers), self.assertRaises(HTTPError) as error:
                        post({'action': 'snapshot'}, headers)
                    self.assertEqual(error.exception.code, 403)
                    error.exception.close()
                with post({'action': 'configure', 'max_size': 960, 'max_fps': 5},
                          {'X-Screen-Token': viewer.token, 'Origin': viewer.url.rstrip('/')}) as response:
                    self.assertEqual(response.status, 202)
                    json.load(response)
                self.assertIn('screen.configure 960 5', drain(control))
                with urlopen(viewer.url) as response:
                    html = response.read()
                    self.assertIn(viewer.token.encode(), html)
                    self.assertNotIn(b'__VIEWER_TOKEN__', html)
                request = Request(viewer.url + 'control', data=b'{' + b'x' * 4096,
                                  headers={'X-Screen-Token': viewer.token,
                                           'Content-Type': 'application/json'})
                with self.assertRaises(HTTPError) as error:
                    urlopen(request)
                self.assertTrue(400 <= error.exception.code < 500)
                error.exception.close()
                self.assertFalse(drain(control))
            finally:
                viewer.close()


if __name__ == '__main__':
    unittest.main()
