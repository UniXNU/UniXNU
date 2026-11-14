#!/usr/bin/env python3
"""Check generic interactive and unattended administrator input."""
import argparse
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import macos_account as account


class AccountInputTest(unittest.TestCase):
    def options(self, *arguments):
        parser = argparse.ArgumentParser()
        account.add_account_arguments(parser)
        return parser, parser.parse_args(arguments)

    def test_command_line_input(self):
        parser, args = self.options('--user', 'admin:fixture:password', '--real-name', 'Admin')
        with patch('builtins.open', side_effect=AssertionError('unexpected terminal access')):
            account.read_account(parser, args)
        self.assertEqual(args.user, 'admin:fixture:password')
        self.assertEqual(args.real_name, 'Admin')

    def test_json_input_and_display_name(self):
        parser, args = self.options('--user-stdin')
        with patch.object(sys, 'stdin', io.StringIO('{"name":"admin","password":"fixture","real_name":"Admin"}')), \
                patch('builtins.open', side_effect=AssertionError('unexpected terminal access')):
            account.read_account(parser, args)
        self.assertEqual(args.user, 'admin:fixture')
        self.assertEqual(args.real_name, 'Admin')

    def test_explicit_display_name_overrides_json(self):
        parser, args = self.options('--user-stdin', '--real-name', 'Operator')
        with patch.object(sys, 'stdin', io.StringIO('{"name":"admin","password":"fixture","real_name":"Admin"}')):
            account.read_account(parser, args)
        self.assertEqual(args.real_name, 'Operator')

    def test_input_modes_are_mutually_exclusive(self):
        with contextlib.redirect_stderr(io.StringIO()) as error, self.assertRaises(SystemExit):
            self.options('--user', 'admin:fixture', '--interactive-user')
        self.assertNotIn('fixture', error.getvalue())

    def test_empty_user_is_refused(self):
        parser, args = self.options('--user', '')
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            account.read_account(parser, args)

    def test_missing_terminal_has_a_clear_error(self):
        parser, args = self.options('--interactive-user')
        with patch('builtins.open', side_effect=OSError('no controlling terminal')), \
                contextlib.redirect_stderr(io.StringIO()) as error, self.assertRaises(SystemExit):
            account.read_account(parser, args)
        self.assertIn('interactive terminal', error.getvalue())

    def test_interactive_prompts_are_device_independent(self):
        class Terminal(io.StringIO):
            def readline(self):
                return '\n'

            def close(self):
                pass

        terminal = Terminal()
        parser, args = self.options('--interactive-user')
        args.skip_setup, args.auto_login = True, True
        with patch('builtins.open', return_value=terminal), patch.object(account.getpass, 'getpass', return_value='fixture'):
            account.read_account(parser, args)
        self.assertEqual((args.user, args.real_name), ('admin:fixture', 'Admin'))
        self.assertIn('Create the macOS administrator', terminal.getvalue())
        self.assertNotIn('sheng', terminal.getvalue())
        self.assertNotIn('VM password', terminal.getvalue())
        self.assertNotIn('fixture', terminal.getvalue())

    def test_no_account_is_still_noninteractive(self):
        parser, args = self.options()
        with patch('builtins.open', side_effect=AssertionError('unexpected terminal access')):
            account.read_account(parser, args)
        self.assertIsNone(args.user)


if __name__ == '__main__':
    unittest.main()
