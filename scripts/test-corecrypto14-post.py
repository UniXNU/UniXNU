#!/usr/bin/env python3
"""Require real crypto registration and refusal of a corrupted POST HMAC."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-existing', action='store_true', help='Validate captured runs without repeating QEMU')
parser.add_argument('--kernel', type=Path, default=ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')
args = parser.parse_args()
kernel = args.kernel.resolve()
original = kernel.read_bytes()
metadata = json.loads(kernel.with_suffix(kernel.suffix + '.crypto-hmac.json').read_text())
if hashlib.sha256(original).hexdigest() != metadata['kernel_sha256']:
    raise SystemExit('The source kernel no longer matches its integrity-build record')
positive = ROOT / 'build/darwinboot-crypto14'
negative = ROOT / 'build/darwinboot-bad-hmac'
bad_path = ROOT / 'build/corecrypto-2023/negative-hmac/kernel.macho'
if not args.check_existing:
    subprocess.run([sys.executable, ROOT / 'scripts/probe-darwinboot-xnu.py', '--kernel', kernel,
                    '--output', positive, '--break-symbol', '_kmem_crypto_init', '--require-crypto14'], check=True)
    bad = bytearray(original)
    bad[int(metadata['hmac_file_offset'], 16)] ^= 1
    bad_path.parent.mkdir(parents=True, exist_ok=True)
    bad_path.write_bytes(bad)
    subprocess.run([sys.executable, ROOT / 'scripts/probe-darwinboot-xnu.py', '--kernel', bad_path,
                    '--output', negative], check=True)
good = json.loads((positive / 'gdb-stop.json').read_text())
bad = json.loads((negative / 'gdb-stop.json').read_text())
corrupted = bad_path.read_bytes()
if len(original) != len(corrupted):
    raise SystemExit('Corruption fixture changed the kernel length')
differences = [index for index, (left, right) in enumerate(zip(original, corrupted)) if left != right]
if differences != [int(metadata['hmac_file_offset'], 16)]:
    raise SystemExit('Negative fixture must change exactly one POST HMAC byte')
if good['kernel_sha256'] != metadata['kernel_sha256'] or not good['crypto14_initialization_observed']:
    raise SystemExit('No matching positive provider initialization was observed')
if good['stop_symbol'] != '_kmem_crypto_init' or not good['native_4k_mmu_observed']:
    raise SystemExit('Positive observation did not reach the expected native 4K stage')
reason = bad['argument_memory'].get('x0', '')
if (bad['kernel_sha256'] != hashlib.sha256(corrupted).hexdigest() or 'FIPS Kernel POST Failed' not in reason
        or bad['crypto14_initialization_observed'] or bad['crypto14_globals']['_g_crypto_funcs']
        or bad['crypto14_globals']['_prng_ready']):
    raise SystemExit('Corrupt HMAC was not refused by the real provider before registration')
report = {'kernel_sha256': metadata['kernel_sha256'], 'native_4k_observed': True,
          'default_provider_post_and_registration_passed': True, 'corrupted_hmac_refused': True,
          'vendor_certification_claimed': False, 'ipados_userspace_boot_demonstrated': False}
(ROOT / 'build/corecrypto-2023/post-test.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS: real provider/PRNG initialization and deliberate HMAC corruption refusal, native 4K retained')
