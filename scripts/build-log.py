#!/usr/bin/env python3
"""Render build status prefixes and keep an uncolored, complete build log."""
import argparse
import codecs
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import sys


ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
PREFIX = re.compile(
    r'^\s*(?:==>?\s+[\w.-]+:?|\d+/\d+ -|Build (?:complete|stopped)|'
    r'Processing|Collecting|Downloading|Looking in (?:indexes|links)|'
    r'Installing (?:collected packages|build dependencies|backend dependencies)|'
    r'Preparing metadata|Getting requirements to build|Building wheels? for collected packages|'
    r'Building wheel for|Attempting uninstall|Found existing installation|Using cached|'
    r'Requirement already satisfied|Checking|Configuring|Generating|Compiling|Linking|patching file|'
    r'Cloning into|Receiving objects|Resolving deltas|Unpacking objects|Updating files|'
    r'IPSW window|(?:OS|SystemOS|App) raw input|Hashing|Images and SHA256SUMS|'
    r'Local PR (?:source|dependency|integration|preparation)|PASS|FAIL|FAILED|ERROR|WARNING|WARN|'
    r'CMake (?:Error|Warning)|unixnu:|'
    r'\*\* (?:BUILD SUCCEEDED|BUILD FAILED) \*\*|\+(?=\s))(?!\w):?', re.IGNORECASE)
TAGS = re.compile(r'\[(INFO|OK|WARN|WARNING|FAILED|ERROR|INPUT|NOTICE|SUCCESS|PASS)\]', re.IGNORECASE)
SUCCESS = re.compile(r'\bSuccess(?:ful(?:ly|l)?)?\b(?: (?:installed|uninstalled|built|downloaded))?', re.IGNORECASE)
DIAGNOSTIC = re.compile(r'\b(?:fatal error|error|warning|note):', re.IGNORECASE)
COLORS = {'info': '\033[94m', 'warning': '\033[93m', 'error': '\033[91m', 'ok': '\033[92m'}
LEVELS = {'ok': 'ok', 'success': 'ok', 'pass': 'ok', 'warn': 'warning', 'warning': 'warning',
          'failed': 'error', 'error': 'error'}


def status_level(text: str) -> str:
    if re.search(r'\b(failed|error|stopped|fail)\b', text, re.IGNORECASE):
        return 'error'
    if re.search(r'\b(warn|warning)\b', text, re.IGNORECASE):
        return 'warning'
    if re.search(r'\b(ok|complete|pass|passed|success|succeeded|done|verified)\b|Using cached|Requirement already satisfied',
                 text, re.IGNORECASE):
        return 'ok'
    return 'info'


def render(text: str, color: bool, line_start: bool = True) -> str:
    if not color:
        return text
    plain = ANSI.sub('', text)
    # Preserve tools that already supply their own colors.
    if plain != text:
        return text
    spans = []
    if line_start and (match := PREFIX.search(text)):
        spans.append((match.start(), match.end(), status_level(text)))
    for match in TAGS.finditer(text):
        spans.append((match.start(), match.end(), LEVELS.get(match[1].lower(), 'info')))
    for match in SUCCESS.finditer(text):
        spans.append((match.start(), match.end(), 'ok'))
    for match in DIAGNOSTIC.finditer(text):
        level = 'warning' if match[0].lower() == 'warning:' else 'info' if match[0].lower() == 'note:' else 'error'
        spans.append((match.start(), match.end(), level))
    result, position = [], 0
    for start, end, level in sorted(spans):
        if start < position:
            continue
        result += [text[position:start], COLORS[level], text[start:end], '\033[0m']
        position = end
    return ''.join(result) + text[position:]


def relay(command: list[str], log_path: Path, color: bool) -> int:
    environment = os.environ.copy()
    environment['UNIXNU_LOG_COLOR'] = '1' if color else '0'
    environment['PYTHONUNBUFFERED'] = '1'
    environment['BUILD_LOG'] = str(log_path)
    # Keep the controlling terminal for interactive tools. The child shares
    # the foreground process group, so terminal signals also reach its descendants.
    child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=environment)
    received = 0

    def interrupt(number, _frame):
        nonlocal received
        received = number
        if child.poll() is None:
            child.send_signal(number)

    previous = {number: signal.signal(number, interrupt) for number in (signal.SIGINT, signal.SIGTERM)}
    decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
    pending = ''
    continuation = False
    try:
        with log_path.open('a', encoding='utf-8', buffering=1) as log, selectors.DefaultSelector() as selector:
            selector.register(child.stdout, selectors.EVENT_READ)

            def output(text, first=True):
                log.write(ANSI.sub('', text))
                log.flush()
                sys.stdout.write(render(text, color, line_start=first))
                sys.stdout.flush()

            while True:
                if not selector.select(timeout=0.15):
                    if pending:
                        output(pending, not continuation)
                        pending = ''
                        continuation = True
                    continue
                block = os.read(child.stdout.fileno(), 65536)
                pending += decoder.decode(block, final=not block)
                while (match := re.search(r'[\r\n]', pending)) is not None:
                    end = match.end()
                    output(pending[:end], not continuation)
                    pending = pending[end:]
                    continuation = False
                if not block:
                    if pending:
                        output(pending, not continuation)
                    break
            result = child.wait()
            return 128 + received if received else 128 - result if result < 0 else result
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)
        child.stdout.close()
        if child.poll() is None:
            child.terminate()
            child.wait()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--color', choices=('auto', 'always', 'never'), default='auto')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a build command is required after --')
    args.log.parent.mkdir(parents=True, exist_ok=True)
    color = not os.environ.get('NO_COLOR') and (args.color == 'always' or args.color == 'auto' and sys.stdout.isatty())
    return relay(command, args.log, color)


if __name__ == '__main__':
    raise SystemExit(main())
