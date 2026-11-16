#!/usr/bin/env python3
"""Download selected GitHub Actions artifact files through ranged ZIP reads."""
import argparse
import io
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
import zlib


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        return None


def download_url(repository, artifact):
    token = subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()
    request = urllib.request.Request(
        f'https://api.github.com/repos/{repository}/actions/artifacts/{artifact}/zip?request_time={time.time_ns()}',
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json', 'Cache-Control': 'no-cache'})
    try:
        urllib.request.build_opener(NoRedirect).open(request, timeout=60)
    except urllib.error.HTTPError as error:
        if error.code in (301, 302, 303, 307, 308):
            url = error.headers['Location']
            if url.startswith('https://'):
                return url
        raise
    raise ValueError('GitHub did not return an artifact download location')


class RangedZip(io.RawIOBase):
    def __init__(self, url, refresh_url=None):
        self.url, self.position, self.small = url, 0, None
        self.refresh_url = refresh_url
        with urllib.request.urlopen(urllib.request.Request(url, headers={'Range': 'bytes=0-0'}), timeout=60) as response:
            match = re.fullmatch(r'bytes 0-0/(\d+)', response.headers.get('Content-Range', ''))
            if response.status != 206 or not match:
                raise ValueError('Artifact storage must support HTTP byte ranges')
            self.size = int(match[1])
        if self.size <= 1024 * 1024:
            self.small = self.read(self.size)
            self.position = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=io.SEEK_SET):
        position = offset + (self.position if whence == io.SEEK_CUR else self.size if whence == io.SEEK_END else 0)
        if position < 0:
            raise ValueError('Negative ZIP position')
        self.position = position
        return position

    def read(self, size=-1):
        size = min(self.size - self.position, size if size >= 0 else self.size)
        if size <= 0:
            return b''
        if self.small is not None:
            data = self.small[self.position:self.position + size]
            self.position += size
            return data
        start, end = self.position, self.position + size - 1
        for attempt in range(3):
            try:
                request = urllib.request.Request(self.url, headers={'Range': f'bytes={start}-{end}'})
                with urllib.request.urlopen(request, timeout=120) as response:
                    if response.status != 206 or response.headers.get('Content-Range') != f'bytes {start}-{end}/{self.size}':
                        raise ValueError('Artifact range response differs from the requested bytes')
                    data = response.read(size)
                if len(data) != size:
                    raise OSError('Artifact range was truncated')
                self.position += size
                return data
            except (OSError, urllib.error.URLError):
                if attempt == 2:
                    raise
                if self.refresh_url:
                    self.url = self.refresh_url()
                time.sleep(attempt + 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', help='OWNER/REPOSITORY; uses the active gh account')
    parser.add_argument('run', type=int)
    parser.add_argument('artifact')
    parser.add_argument('output', type=Path)
    parser.add_argument('--file', action='append', help='exact archive path; repeat to select files')
    args = parser.parse_args()
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', args.repository):
        parser.error('repository must be OWNER/REPOSITORY')
    result = json.loads(subprocess.check_output([
        'gh', 'api', f'repos/{args.repository}/actions/runs/{args.run}/artifacts?per_page=100']))
    matches = [item for item in result['artifacts'] if item['name'] == args.artifact and not item['expired']]
    if len(matches) != 1:
        parser.error('require one unexpired artifact with the selected name')
    refresh = lambda: download_url(args.repository, matches[0]['id'])
    with RangedZip(refresh(), refresh) as source, zipfile.ZipFile(source) as archive:
        selected = args.file or [item.filename for item in archive.infolist() if not item.is_dir()]
        for name in selected:
            relative = Path(name)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Artifact path escapes the output directory')
            target = args.output / relative
            if target.exists():
                raise FileExistsError('Choose a new output directory: ' + str(target))
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + '.download')
            info, position, crc = archive.getinfo(name), 0, 0
            if temporary.exists():
                with temporary.open('rb') as previous:
                    for data in iter(lambda: previous.read(64 * 1024 * 1024), b''):
                        position += len(data)
                        crc = zlib.crc32(data, crc)
                if position > info.file_size:
                    raise ValueError('Partial download exceeds the selected artifact file')
                print(f'{target}: resuming at {position} bytes', flush=True)
            with archive.open(name) as incoming, temporary.open('ab') as outgoing:
                incoming.seek(position)
                for data in iter(lambda: incoming.read(64 * 1024 * 1024), b''):
                    outgoing.write(data)
                    position += len(data)
                    crc = zlib.crc32(data, crc)
            if position != info.file_size or crc != info.CRC:
                raise zipfile.BadZipFile('Downloaded file differs from the ZIP entry: ' + name)
            temporary.replace(target)
            print(f'{target}: {target.stat().st_size} bytes', flush=True)


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as error:
        raise SystemExit(f'Artifact download HTTP error {error.code}') from None
    except urllib.error.URLError:
        raise SystemExit('Artifact download connection failed') from None
