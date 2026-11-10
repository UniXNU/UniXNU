#!/usr/bin/env python3
"""Sign the root windows of an OS profile with an owner key and verify every block with the C provider.

    make-root-policies.py --tree TREE --output POLICIES --window NAME=IMAGE:VOLUME_UUID [--window ...]

IMAGE is the window's disk image exactly as the userdata image carries it (a raw APFS container or raw
disk). Each window gets POLICIES/NAME/{manifest.header.bin,trusted-key.bin,verification.json}: the
544-byte signed header that goes into the boot image, the owner anchor and the verification record.
The hash table of each window stays in TREE/build/verified-root-NAME/hashes.bin, the userdata object
NAME.vroot. The owner key pair is made once in TREE/build/verified-root-host/keys (never committed);
all windows of one run share it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]


def openssl_prefix():
    for candidate in ('/opt/homebrew/opt/openssl@3', '/usr/local/opt/openssl@3', '/usr'):
        if (Path(candidate) / 'include/openssl/evp.h').is_file():
            return Path(candidate)
    raise SystemExit('OpenSSL 3 headers not found (brew install openssl@3)')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--window', action='append', required=True, metavar='NAME=IMAGE:VOLUME_UUID')
    parser.add_argument('--generation', type=int, default=1)
    args = parser.parse_args()
    kit = ROOT / 'kits/VerifiedRoot'
    host = args.tree.resolve() / 'build/verified-root-host'
    # check.py makes the owner keys once (0600, in a 0700 directory) and builds the host verifier.
    subprocess.run([sys.executable, str(kit / 'tests/check.py'), '--output', str(host),
                    '--openssl-prefix', str(openssl_prefix())], check=True, stdout=subprocess.DEVNULL)
    keys = host / 'keys'
    anchors = set()
    for spec in args.window:
        name, sep, rest = spec.partition('=')
        image_text, sep2, volume = rest.rpartition(':')
        if not sep or not sep2 or not name or '/' in name:
            parser.error(f'--window {spec}: expected NAME=IMAGE:VOLUME_UUID')
        image, volume = Path(image_text).resolve(), str(uuid.UUID(volume)).upper()
        if not image.is_file():
            parser.error(f'{image}: not a regular file')
        work = args.tree.resolve() / f'build/verified-root-{name}'
        if work.exists():
            shutil.rmtree(work)
        subprocess.run([sys.executable, str(kit / 'tools/manifest.py'), '--image', str(image),
                        '--private-key', str(keys / 'owner.pem'), '--public-key', str(keys / 'owner-public.pem'),
                        '--volume-uuid', volume, '--generation', str(args.generation), '--output', str(work)],
                       check=True, stdout=subprocess.DEVNULL)
        report = work / 'verification.json'
        subprocess.run([sys.executable, str(kit / 'tools/verify_image.py'), '--library', str(host / 'verified-root.dylib'),
                        '--manifest', str(work / 'manifest.bin'), '--trusted-key', str(work / 'trusted-key.bin'),
                        '--image', str(image), '--volume-uuid', volume, '--minimum-generation', str(args.generation),
                        '--output', str(report)], check=True)
        envelope = (work / 'manifest.bin').read_bytes()
        record = json.loads(report.read_text())
        if (record['volume_uuid'] != volume or envelope[56:88].hex() != record['image_sha256'] or
                len(envelope) != 544 + 32 * record['blocks_verified']):
            raise SystemExit(f'{name}: the signed manifest does not describe {image}')
        destination = args.output / name
        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'manifest.header.bin').write_bytes(envelope[:544])
        shutil.copyfile(work / 'trusted-key.bin', destination / 'trusted-key.bin')
        shutil.copyfile(report, destination / 'verification.json')
        anchors.add(hashlib.sha256((work / 'trusted-key.bin').read_bytes()).hexdigest())
        print(f'{name}: {record["blocks_verified"]} blocks, image {record["image_sha256"]}, '
              f'table {work / "hashes.bin"} ({name}.vroot)')
    if len(anchors) != 1:
        raise SystemExit('the windows were not signed by one owner key')


if __name__ == '__main__':
    main()
