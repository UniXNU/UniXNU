#!/usr/bin/env python3
"""Download selected GitHub Actions artifact files through ranged ZIP reads."""
import argparse
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import zipfile


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        return None


def download_url(repository, artifact):
    token = subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()
    request = urllib.request.Request(
        f'https://api.github.com/repos/{repository}/actions/artifacts/{artifact}/zip',
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json'})
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
    def __init__(self, url):
        self.url, self.position = url, 0
        with urllib.request.urlopen(urllib.request.Request(url, headers={'Range': 'bytes=0-0'}), timeout=60) as response:
            match = re.fullmatch(r'bytes 0-0/(\d+)', response.headers.get('Content-Range', ''))
            if response.status != 206 or not match:
                raise ValueError('Artifact storage must support HTTP byte ranges')
            self.size = int(match[1])

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
    with RangedZip(download_url(args.repository, matches[0]['id'])) as source, zipfile.ZipFile(source) as archive:
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
            with archive.open(name) as incoming, temporary.open('wb') as outgoing:
                shutil.copyfileobj(incoming, outgoing, length=64 * 1024 * 1024)
            temporary.replace(target)
            print(f'{target}: {target.stat().st_size} bytes', flush=True)


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as error:
        raise SystemExit(f'Artifact download HTTP error {error.code}') from None
    except urllib.error.URLError:
        raise SystemExit('Artifact download connection failed') from None
