#!/usr/bin/env python3
"""Restore omitted DriverKit headers from Apple's earlier Darwin 23 source."""
import concurrent.futures
import hashlib
import http.client
import json
import os
from pathlib import Path
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request

# Tags of the Apple sources that still carry the headers newer xnu omits; feeds.toml sets them for the unixnu driver.
TAG = os.environ.get('UNIXNU_DRIVERKIT_TAG', 'xnu-10063.121.3')
TRUST_TAG = os.environ.get('UNIXNU_TRUSTCACHE_TAG', 'xnu-8796.101.5')
DESTINATION = Path('.cache/xnu-work/iokit/DriverKit')
CACHE = Path(f'.cache/sources/xnu-driverkit-{TAG.removeprefix("xnu-")}.json')
# Anonymous GitHub API calls share a small per-address quota that hosted CI runners exhaust (HTTP 403);
# a token in GITHUB_TOKEN or GH_TOKEN is sent to GitHub hosts only.
TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'unixnu-prepare-xnu-source'})
    if TOKEN and urllib.parse.urlsplit(url).hostname in ('api.github.com', 'raw.githubusercontent.com'):
        request.add_header('Authorization', f'Bearer {TOKEN}')
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


def archive_entries(directory, tag):
    """Use the same Apple source tag when GitHub's directory API is rate limited."""
    archive = CACHE.parent / f'xnu-public-headers-{tag}.tar.gz'
    if not archive.exists():
        print(f'Fetching public headers - Apple {tag} archive', flush=True)
        data = fetch(f'https://codeload.github.com/apple-oss-distributions/xnu/tar.gz/refs/tags/{urllib.parse.quote(tag, safe="")}')
        archive.parent.mkdir(parents=True, exist_ok=True)
        temporary = archive.with_suffix('.part')
        temporary.write_bytes(data)
        with tarfile.open(temporary, 'r:gz') as source:
            source.getmembers()
        temporary.replace(archive)
    entries = []
    with tarfile.open(archive, 'r:gz') as source:
        for member in source:
            relative = member.name.partition('/')[2]
            if not member.isfile() or not relative.startswith(directory + '/'):
                continue
            name = relative[len(directory) + 1:]
            if '/' in name or not name.endswith('.h'):
                continue
            data = source.extractfile(member).read()
            entries.append({'type': 'file', 'name': name,
                            'sha': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(),
                            'download_url': f'https://raw.githubusercontent.com/apple-oss-distributions/xnu/{tag}/{relative}'})
    if not entries:
        raise ValueError(f'No public headers in Apple {tag}: {directory}')
    return entries


def directory_entries(cache, directory, tag):
    if cache.exists():
        return json.loads(cache.read_text())
    url = ('https://api.github.com/repos/apple-oss-distributions/xnu/contents/'
           f'{directory}?ref={urllib.parse.quote(tag, safe="")}')
    try:
        entries = json.loads(fetch(url))
    except urllib.error.HTTPError as error:
        if error.code not in (403, 429):
            raise
        print(f'GitHub directory API limited - using Apple {tag} archive for {directory}', flush=True)
        entries = archive_entries(directory, tag)
    if not isinstance(entries, list):
        raise ValueError(f'Unexpected GitHub directory response: {directory}')
    cache.parent.mkdir(parents=True, exist_ok=True)
    temporary = cache.with_suffix('.tmp')
    temporary.write_text(json.dumps(entries) + '\n')
    temporary.replace(cache)
    return entries


def restore(entry, destination=DESTINATION, tag=TAG):
    if entry['type'] != 'file' or not entry['name'].endswith('.h'):
        return None
    name = entry.get('relative', entry['name'])
    target = destination / name
    if target.exists():
        return None
    data = fetch(entry['download_url'])
    digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if digest != entry['sha']:
        raise ValueError(f'Git blob hash mismatch: {entry["name"]}')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return {'name': name, 'source_tag': tag, 'git_blob': digest,
            'sha256': hashlib.sha256(data).hexdigest()}


if __name__ == '__main__':
    if not DESTINATION.is_dir():
        raise SystemExit('Create the local XNU work source before preparing headers')
    entries = directory_entries(CACHE, 'iokit/DriverKit', TAG)
    crypto_cache = CACHE.with_name(f'xnu-driverkit-crypto-{TAG.removeprefix("xnu-")}.json')
    for entry in directory_entries(crypto_cache, 'iokit/DriverKit/crypto', TAG):
        entry['relative'] = 'crypto/' + entry['name']
        entries.append(entry)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        restored = [entry for entry in executor.map(restore, entries) if entry]
        trust_tag = TRUST_TAG
        trust_cache = CACHE.with_name(f'xnu-trustcache-{TRUST_TAG.removeprefix("xnu-")}.json')
        trust_destination = Path('.cache/xnu-work/EXTERNAL_HEADERS/TrustCache')
        def restore_trust(entry):
            return restore(entry, trust_destination, trust_tag)
        restored.extend(entry for entry in executor.map(
            restore_trust, directory_entries(trust_cache, 'EXTERNAL_HEADERS/TrustCache', trust_tag)) if entry)
    previous = Path('.cache/sources/xnu-restored-headers.json')
    existing = json.loads(previous.read_text()) if previous.exists() else []
    by_name = {entry['name']: entry for entry in existing + restored}
    previous.write_text(json.dumps(list(by_name.values()), indent=2) + '\n')
    print(f'Restored {len(restored)} omitted public headers from Apple; blob hashes verified')
