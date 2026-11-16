#!/usr/bin/env python3
"""Build locally with an exported iPhoneOS SDK and kernel tools."""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--tools', type=Path, required=True)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
    if not arguments:
        parser.error('pass unixnu build arguments after --')
    subprocess.run([str(ROOT / 'unixnu'), *arguments, '--kernel-sdk', str(args.sdk.resolve()),
                    '--kernel-tools', str(args.tools.resolve())], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
