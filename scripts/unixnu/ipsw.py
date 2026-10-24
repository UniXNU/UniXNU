"""The target OS image (IPSW): a local file or a remote URL, read member by member.

A remote IPSW is never downloaded as a whole. The zip directory and the members that are needed are read
with HTTP range requests, so the same code serves a local file and an https URL. Members are cached under
out/ipsw/<build>/ with their sha256, and checked against the pins of board.toml [ipsw.sha256] when given.

The board describes the image in [ipsw]: url (the default remote source), product, version, build, device_class,
chip_id, board_id, and the components the steps use.
"""
import hashlib
import io
import json
import platform
import plistlib
import struct
import subprocess
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
        self.url, self.block, self.retries = url, block, retries
        self.position = 0
        self.cache = {}
        request = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(request, timeout=60) as response:
            self.size = int(response.headers['Content-Length'])
        probe = urllib.request.Request(url, headers={'Range': 'bytes=0-0'})
        with urllib.request.urlopen(probe, timeout=60) as response:
            if response.status != 206:
                raise Error(f'{url} does not support range requests')

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
            if len(self.cache) >= 4:
                self.cache.pop(next(iter(self.cache)))
            start = index * self.block
            end = min(start + self.block, self.size) - 1
            for attempt in range(self.retries):
                try:
                    request = urllib.request.Request(self.url, headers={'Range': f'bytes={start}-{end}'})
                    with urllib.request.urlopen(request, timeout=120) as response:
                        data = response.read()
                    if len(data) != end - start + 1:
                        raise OSError('short range response')
                    self.cache[index] = data
                    break
                except (OSError, urllib.error.URLError):
                    if attempt == self.retries - 1:
                        raise
                    time.sleep(2 ** attempt)
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
        with self.zip.open(name) as source, partial.open('wb') as target:
            while chunk := source.read(CHUNK):
                target.write(chunk)
                digest.update(chunk)
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
