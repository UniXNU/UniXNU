"""The target OS image (IPSW): a local file or a remote URL, read member by member.

A remote IPSW is never downloaded as a whole. The zip directory and the members that are needed are read
with HTTP range requests, so the same code serves a local file and an https URL. Members are cached under
out/ipsw/<build>/ with their sha256, and checked against the pins of board.toml [ipsw.sha256] when given.

The board describes the image in [ipsw]: url (the default remote source), product, version, build, device_class,
chip_id, board_id, and the components the steps use.
"""
import concurrent.futures
import contextlib
import hashlib
import http.client
import io
import json
import os
import platform
import plistlib
import struct
import subprocess
import threading
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from .util import Error, expand, log, lzfse, sha256_file, tool

CHUNK = 8 << 20


class RangeFile(io.RawIOBase):
    """A read-only seekable view of a remote file, fetched with HTTP range requests and a small block cache."""

    def __init__(self, url, block=CHUNK, retries=4):
        if block <= 0 or retries <= 0:
            raise ValueError('range block size and attempts must be positive')
        self.url, self.block, self.retries = url, block, retries
        self.position = 0
        self.cache = {}
        self._prefetch = None
        self.size = self._request()
        self._request(0, 0)

    def _request(self, start=None, end=None, stop=None):
        """Retry a complete range; truncated bytes never enter the seekable cache."""
        headers = {'Accept-Encoding': 'identity'}
        if start is not None:
            headers['Range'] = f'bytes={start}-{end}'
        label = 'size query' if start is None else f'bytes {start}-{end}'
        for attempt in range(self.retries):
            if stop is not None and stop.is_set():
                raise concurrent.futures.CancelledError()
            try:
                request = urllib.request.Request(self.url, headers=headers, method='HEAD' if start is None else 'GET')
                with urllib.request.urlopen(request, timeout=30 if stop is not None else 60 if start is None else 120) as response:
                    if start is None:
                        try:
                            size = int(response.headers['Content-Length'])
                        except (KeyError, TypeError, ValueError) as error:
                            raise OSError('missing or invalid IPSW Content-Length') from error
                        if response.status != 200 or size <= 0:
                            raise OSError('invalid IPSW size response')
                        return size
                    expected = end - start + 1
                    if response.status != 206:
                        raise OSError('server did not return HTTP 206 for the requested range')
                    if response.headers.get('Content-Range') != f'bytes {start}-{end}/{self.size}':
                        raise OSError('Content-Range differs from the requested IPSW range')
                    length = response.headers.get('Content-Length')
                    if length is not None and length != str(expected):
                        raise OSError('Content-Length differs from the requested IPSW range')
                    if stop is None:
                        data = response.read(expected + 1)
                    else:
                        data = bytearray()
                        deadline = time.monotonic() + 120
                        while len(data) < expected:
                            if stop.is_set():
                                raise concurrent.futures.CancelledError()
                            if time.monotonic() >= deadline:
                                raise TimeoutError('range transfer exceeded 120s')
                            chunk = response.read1(min(65536, expected - len(data)))
                            if not chunk:
                                break
                            data.extend(chunk)
                        data = bytes(data)
                    if len(data) != expected:
                        raise OSError(f'short range response: received {len(data)} of {expected} bytes')
                    return data
            except (OSError, http.client.HTTPException) as error:
                if isinstance(error, urllib.error.HTTPError):
                    error.close()
                    if error.code not in (408, 425, 429, 500, 502, 503, 504):
                        raise Error(f'IPSW {label} failed: HTTP {error.code} {error.reason}') from error
                if attempt + 1 == self.retries:
                    raise Error(f'IPSW {label} failed after {self.retries} attempts: {error}') from error
                delay = 2 ** attempt
                log(f'ipsw: warning - {label} - {type(error).__name__}: {error} - '
                    f'retry {attempt + 2}/{self.retries} in {delay}s')
                if stop is None:
                    time.sleep(delay)
                elif stop.wait(delay):
                    raise concurrent.futures.CancelledError()

    @contextlib.contextmanager
    def prefetch(self, start, length, workers=64):
        """Fetch only the active ZIP member, with at most one queued block per worker."""
        if not 1 <= workers <= 64 or start < 0 or length < 0 or start + length > self.size:
            raise Error('invalid IPSW parallel range window')
        if self._prefetch is not None:
            raise Error('nested IPSW prefetch windows are not supported')
        first = start // self.block
        end = (start + length + self.block - 1) // self.block
        workers = min(workers, end - first) if length else 1
        if workers <= 1:
            yield 1
            return
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=workers, thread_name_prefix='ipsw-range')
        state = {'pool': pool, 'stop': threading.Event(), 'pending': {}, 'next': first,
                 'end': end, 'workers': workers}
        self._prefetch = state
        try:
            self._fill_prefetch()
            yield workers
        finally:
            state['stop'].set()
            for future in state['pending'].values():
                future.cancel()
            pool.shutdown(wait=True, cancel_futures=True)
            self._prefetch = None

    def _fill_prefetch(self):
        state = self._prefetch
        while state['next'] < state['end'] and len(state['pending']) < state['workers']:
            index = state['next']
            state['next'] += 1
            if index in self.cache:
                continue
            start = index * self.block
            end = min(start + self.block, self.size) - 1
            state['pending'][index] = state['pool'].submit(self._request, start, end, state['stop'])

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        self.position = {0: offset, 1: self.position + offset, 2: self.size + offset}[whence]
        return self.position

    def _block(self, index):
        if index not in self.cache:
            start = index * self.block
            end = min(start + self.block, self.size) - 1
            pending = self._prefetch['pending'] if self._prefetch is not None else {}
            future = pending.get(index)
            data = future.result() if future is not None else self._request(start, end)
            if future is not None:
                del pending[index]
            if len(self.cache) >= 4:
                self.cache.pop(next(iter(self.cache)))
            self.cache[index] = data
            if future is not None:
                self._fill_prefetch()
        return self.cache[index]

    def readinto(self, buffer):
        want = min(len(buffer), self.size - self.position)
        done = 0
        while done < want:
            index, inside = divmod(self.position, self.block)
            data = self._block(index)[inside:inside + want - done]
            buffer[done:done + len(data)] = data
            done += len(data)
            self.position += len(data)
        return done


def spec_of(ctx):
    """The source: --ipsw, UNIXNU_IPSW, or the url of board.toml [ipsw]. A URL is remote, anything else a local path."""
    spec = ctx.option_text('ipsw', 'UNIXNU_IPSW') or ctx.board.get('ipsw', {}).get('url')
    if not spec:
        raise Error('no IPSW: pass --ipsw PATH_OR_URL (or UNIXNU_IPSW), or set url in board.toml [ipsw]')
    return spec


class Ipsw:
    def __init__(self, ctx, spec=None):
        self.ctx = ctx
        self.config = ctx.board.get('ipsw')
        if not self.config:
            raise Error('board.toml has no [ipsw]')
        self.spec = spec or spec_of(ctx)
        self.remote = self.spec.startswith(('http://', 'https://'))
        try:
            self.jobs = int(os.environ.get('UNIXNU_IPSW_JOBS', '64'))
        except ValueError as error:
            raise Error('UNIXNU_IPSW_JOBS must be an integer in 1..64') from error
        if not 1 <= self.jobs <= 64:
            raise Error('UNIXNU_IPSW_JOBS must be in 1..64')
        if self.remote:
            log(f'ipsw: remote {self.spec}')
            self.stream = RangeFile(self.spec)
        else:
            path = expand(self.spec)
            if not path.is_file():
                raise Error(f'IPSW not found: {path}')
            log(f'ipsw: local {path}')
            self.stream = path.open('rb')
        self.zip = zipfile.ZipFile(self.stream)
        self.manifest = plistlib.loads(self.zip.read('BuildManifest.plist'))
        self.identity = self._identity()
        self.cache = ctx.out_root / 'ipsw' / self.config['build']

    def _identity(self):
        c, m = self.config, self.manifest
        if (m['ProductVersion'], m['ProductBuildVersion']) != (c['version'], c['build']) or c['product'] not in m['SupportedProductTypes']:
            raise Error(f'this IPSW is {m["ProductVersion"]} ({m["ProductBuildVersion"]}) for {", ".join(m["SupportedProductTypes"])}; '
                        f'the board expects {c["version"]} ({c["build"]}) for {c["product"]}')
        for item in m['BuildIdentities']:
            if (item['Info']['DeviceClass'] == c['device_class'] and item['Info']['RestoreBehavior'] == 'Erase'
                    and int(item['ApChipID'], 16) == c['chip_id'] and int(item['ApBoardID'], 16) == c['board_id']):
                return item
        raise Error(f'no Erase build identity for {c["device_class"]} in this IPSW')

    def member(self, component):
        try:
            return self.identity['Manifest'][component]['Info']['Path']
        except KeyError:
            raise Error(f'component {component} is not in this IPSW') from None

    def info(self, component):
        name = self.member(component)
        entry = self.zip.getinfo(name)
        return name, entry.file_size, entry.compress_size

    def extract(self, component):
        """Extract a component into the cache (skipped when it is there and matches its pin); returns its path."""
        name, size, _ = self.info(component)
        destination = self.cache / Path(name).name
        pin = self.config.get('sha256', {}).get(Path(name).name)
        record = destination.with_suffix(destination.suffix + '.json')
        if destination.is_file() and destination.stat().st_size == size:
            if pin is None or (record.is_file() and json.loads(record.read_text()).get('sha256') == pin) or sha256_file(destination) == pin:
                return destination
            destination.unlink()
        self.cache.mkdir(parents=True, exist_ok=True)
        partial = destination.with_suffix(destination.suffix + '.partial')
        digest = hashlib.sha256()
        log(f'ipsw: extracting {component} ({name}, {size >> 20} MiB)')
        started = reported = time.monotonic()
        done = 0
        with self.zip.open(name) as source, partial.open('wb') as target:
            # ZipFile.open has consumed the local header, so tell() is the first compressed byte.
            window = (self.stream.prefetch(self.stream.tell(), self.zip.getinfo(name).compress_size, self.jobs)
                      if isinstance(getattr(self, 'stream', None), RangeFile) else contextlib.nullcontext(1))
            with window as jobs:
                if self.remote:
                    log(f'ipsw: {component} - up to {jobs} parallel ranges - {CHUNK >> 20} MiB per range')
                while chunk := source.read(CHUNK):
                    target.write(chunk)
                    digest.update(chunk)
                    done += len(chunk)
                    now = time.monotonic()
                    if now - reported >= 10 or done == size:
                        elapsed = max(now - started, 0.001)
                        speed = done / elapsed
                        eta = int((size - done) / speed) if speed else 0
                        log(f'ipsw: {component} - {100 * done / size:.1f}% - {done / (1 << 20):.1f}/{size / (1 << 20):.1f} MiB - '
                            f'{speed / (1 << 20):.1f} MiB/s - elapsed {int(elapsed)}s - ETA {eta}s')
                        reported = now
        if partial.stat().st_size != size:
            partial.unlink()
            raise Error(f'incomplete extraction of {name}')
        if pin and digest.hexdigest() != pin:
            partial.unlink()
            raise Error(f'{name} differs from the pinned sha256 of board.toml [ipsw.sha256]: {digest.hexdigest()}')
        partial.rename(destination)
        record.write_text(json.dumps({'component': component, 'member': name, 'size': size, 'sha256': digest.hexdigest(),
                                      'source': 'remote' if self.remote else 'local'}, indent=2) + '\n')
        return destination

    def read(self, component):
        return self.zip.read(self.member(component))

    def disk_image(self, component):
        """A component as a plain disk image: extracted, then decrypted when the IPSW ships it as AEA."""
        # AEA inputs may have been removed after decryption. Validate the plain
        # image and both recorded identities before downloading the archive again.
        name = self.member(component)
        if name.endswith('.aea'):
            archive = self.cache / Path(name).name
            plain = archive.with_suffix('')
            record = plain.with_suffix(plain.suffix + '.json')
            origin = archive.with_suffix(archive.suffix + '.json')
            if plain.is_file() and record.is_file() and origin.is_file():
                data, source = json.loads(record.read_text()), json.loads(origin.read_text())
                pin = self.config.get('sha256', {}).get(archive.name)
                if source.get('member') == name and data.get('member') == name \
                        and data.get('aea_sha256') == source.get('sha256') \
                        and (pin is None or pin == source.get('sha256')) \
                        and data.get('size') == plain.stat().st_size \
                        and sha256_file(plain) == data.get('sha256'):
                    return plain
        path = self.extract(component)
        if path.suffix != '.aea':
            return path
        return decrypt_aea(path)


def decrypt_aea(path):
    """Decrypt an AEA archive beside it (name without .aea), cached with the sha256 of both files.

    The key is fetched by `ipsw fw aea --key` from the key URL in the archive header and passed to macOS aea;
    it is not written to disk or the log.
    """
    out = path.with_suffix('')
    record = out.with_suffix(out.suffix + '.json')
    if out.is_file() and record.is_file():
        data = json.loads(record.read_text())
        if data.get('aea_sha256') == json.loads(path.with_suffix(path.suffix + '.json').read_text()).get('sha256') \
                and data.get('size') == out.stat().st_size:
            return out
    if platform.system() != 'Darwin':
        raise Error(f'{path.name} is AEA encrypted; decrypting it needs macOS /usr/bin/aea')
    tool('aea', 'macOS /usr/bin/aea decrypts AEA disk images')
    ipsw = tool('ipsw', 'the ipsw tool fetches the AEA key (brew install blacktop/tap/ipsw)')
    log(f'ipsw: fetching the AEA key of {path.name}')
    result = subprocess.run([ipsw, 'fw', 'aea', '--key', str(path)], capture_output=True, text=True)
    keys = [line.strip() for line in result.stdout.splitlines() if line.strip().startswith('base64:')]
    if result.returncode or len(keys) != 1:
        raise Error(f'could not fetch the AEA key of {path.name}: {result.stderr.strip()[-300:]}')
    partial = out.with_suffix(out.suffix + '.partial')
    log(f'ipsw: decrypting {path.name}')
    result = subprocess.run(['/usr/bin/aea', 'decrypt', '-i', str(path), '-o', str(partial), '-key-value', keys[0]],
                            capture_output=True, text=True)
    if result.returncode:
        partial.unlink(missing_ok=True)
        raise Error(f'aea decrypt of {path.name} failed: {result.stderr.strip()[-300:]}')
    partial.rename(out)
    source = json.loads(path.with_suffix(path.suffix + '.json').read_text())
    record.write_text(json.dumps({'member': source.get('member'), 'aea_sha256': source.get('sha256'),
                                  'size': out.stat().st_size, 'sha256': sha256_file(out)}, indent=2) + '\n')
    return out


def _der(data, at):
    tag, length = data[at], data[at + 1]
    at += 2
    if length & 0x80:
        count = length & 0x7f
        length = int.from_bytes(data[at:at + count], 'big')
        at += count
    return tag, at, length


def im4p_payload(data):
    """The payload of an IM4P (DER: IM4P, type, version, data, ...)."""
    tag, start, length = _der(data, 0)
    if tag != 0x30:
        raise Error('not an IM4P')
    at, items = start, []
    while at < start + length:
        _, body, size = _der(data, at)
        items.append(data[body:body + size])
        at = body + size
    if len(items) < 4 or items[0] != b'IM4P':
        raise Error('not an IM4P')
    return items[3]


def kernelcache(ctx, source):
    """The decompressed arm64 kernelcache Mach-O of the IPSW, in out/ipsw (checked against the board pin)."""
    spec = ctx.board.get('kernel', {}).get('prelink', {})
    out = source.cache / 'kernelcache.decompressed'
    pin = spec.get('kernelcache_sha256')
    if out.is_file() and (pin is None or sha256_file(out) == pin):
        return out
    if platform.system() == 'Linux':
        decode = [lzfse(), '-decode']
    else:
        tool('compression_tool', 'macOS /usr/bin/compression_tool decodes the LZFSE kernelcache')
        decode = ['/usr/bin/compression_tool', '-decode', '-a', 'lzfse']
    source.cache.mkdir(parents=True, exist_ok=True)
    payload = im4p_payload(source.read('KernelCache'))
    packed, raw = source.cache / 'kernelcache.lzfse', source.cache / 'kernelcache.fat'
    packed.write_bytes(payload)
    result = subprocess.run([*decode, '-i', packed, '-o', raw], capture_output=True, text=True)
    if result.returncode:
        raise Error(f'{Path(decode[0]).name} failed: {result.stderr.strip()}')
    fat = raw.read_bytes()
    if fat[:4] == b'\xca\xfe\xba\xbe':
        count = struct.unpack('>I', fat[4:8])[0]
        slices = [struct.unpack('>5I', fat[8 + 20 * i:28 + 20 * i]) for i in range(count)]
        arm64 = [s for s in slices if s[0] == 0x0100000c]
        if len(arm64) != 1:
            raise Error('expected exactly one arm64 slice in the kernelcache')
        _, _, offset, size, _ = arm64[0]
        fat = fat[offset:offset + size]
    packed.unlink()
    raw.unlink()
    if fat[:4] != b'\xcf\xfa\xed\xfe':
        raise Error('the decompressed kernelcache is not a 64-bit Mach-O')
    out.write_bytes(fat)
    if pin and sha256_file(out) != pin:
        out.unlink()
        raise Error(f'the kernelcache of this IPSW does not match the pin of board.toml (sha256 {pin})')
    return out
