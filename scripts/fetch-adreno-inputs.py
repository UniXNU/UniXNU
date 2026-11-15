#!/usr/bin/env python3
"""Fetch only SHA-pinned Adreno source and firmware; never execute firmware."""
import base64
import concurrent.futures
import hashlib
import http.client
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
pins = json.loads((ROOT / 'scripts/data/adreno-inputs.json').read_text())


# Anonymous GitHub API calls share a small per-address quota that hosted CI runners exhaust
# (HTTP 403); a token in GITHUB_TOKEN or GH_TOKEN is sent to GitHub hosts only.
TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')


def download(url):
    headers = {'User-Agent': 'unixnu-adreno-inputs'}
    if TOKEN and urllib.parse.urlsplit(url).hostname in ('api.github.com', 'raw.githubusercontent.com'):
        headers['Authorization'] = f'Bearer {TOKEN}'
    request = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read()
        except (OSError, EOFError, http.client.IncompleteRead) as error:
            if isinstance(error, urllib.error.HTTPError) and error.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def fetch(item):
    path, url, expected, blob, encoding = item
    if path.exists():
        data = path.read_bytes()
    else:
        data = download(url)
        if encoding == 'github-blob':
            data = base64.b64decode(json.loads(data)['content'])
        elif encoding == 'gitiles-base64':
            data = base64.b64decode(data, validate=False)
    if hashlib.sha256(data).hexdigest() != expected['sha256'] or (expected.get('bytes') and len(data) != expected['bytes']):
        raise ValueError('Pinned input hash/size differs: ' + path.name)
    if blob and hashlib.sha1(('blob ' + str(len(data)) + '\0').encode() + data).hexdigest() != blob:
        raise ValueError('Pinned Git blob identity differs: ' + path.name)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + '.part')
        temporary.write_bytes(data)
        temporary.replace(path)
    return len(data)


if __name__ == '__main__':
    jobs = []
    linux = pins['linux']
    for name, expected in linux['files'].items():
        url = linux['repository'].replace('https://github.com/', 'https://raw.githubusercontent.com/') + '/' + linux['commit'] + '/' + name
        jobs.append((ROOT / '.cache/adreno-source' / name, url, expected, None, None))
    mesa = pins['mesa']
    for name, expected in mesa['files'].items():
        url = mesa['mirror'] + '/+/' + mesa['commit'] + '/' + name + '?format=TEXT'
        jobs.append((ROOT / '.cache/adreno-source/mesa' / name, url, expected, None, 'gitiles-base64'))
    firmware = pins['firmware']
    for name, expected in firmware['files'].items():
        blob = expected['git_blob_sha1']
        url = (firmware['repository'].replace('https://github.com/', 'https://raw.githubusercontent.com/')
               + '/' + firmware['tree_sha'] + '/' + name)
        jobs.append((ROOT / '.cache/firmware/sheng-gpu' / name, url, expected, blob, None))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        sizes = list(executor.map(fetch, jobs))
    print(f'PASS: {len(sizes)} exact source/firmware inputs, {sum(sizes)} bytes; no GPU execution/authenticity claim')
