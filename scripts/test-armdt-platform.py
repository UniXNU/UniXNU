#!/usr/bin/env python3
"""Qualify the generic ArmDTPlatform expert under the real QEMU UEFI/XNU path.

The QEMU fixture supplies actual QEMU virt GICv3 resources and a CHRP NVRAM
proxy around the generic `device-tree` platform root. It says nothing about
sheng hardware. Both observations must show native 4K translation and the real
source crypto provider before platform matching.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-existing', action='store_true',
                    help='Verify the retained reports without another QEMU run')
parser.add_argument('--configure-only', action='store_true',
                    help='Run only the platform configure observation')
args = parser.parse_args()

configure = ROOT / 'build/darwinboot-armdt-platform'
bsd = ROOT / 'build/darwinboot-armdt-bsd'
kernel = ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped'

if not args.check_existing:
    subprocess.run(['python3', ROOT / 'scripts/probe-darwinboot-xnu.py',
                    '--armvirt', '--armcpu', '--nvram-proxy', '--require-crypto14',
                    '--break-symbol', '__ZN13ArmDTPlatform9configureEP9IOService',
                    '--finish-function', '--output', configure], check=True)
    if not args.configure_only:
        subprocess.run(['python3', ROOT / 'scripts/probe-darwinboot-xnu.py',
                        '--armvirt', '--armcpu', '--nvram-proxy', '--require-crypto14',
                        '--break-symbol', '_bsd_init', '--timeout', '40',
                        '--output', bsd], check=True)

reports = [configure] + ([] if args.configure_only else [bsd])
loaded = {}
for directory in reports:
    path = directory / 'gdb-stop.json'
    if not path.exists():
        raise SystemExit(f'Missing retained report: {path}')
    loaded[directory.name] = json.loads(path.read_text())

hashes = {report['kernel_sha256'] for report in loaded.values()}
if len(hashes) != 1:
    raise SystemExit('Observations must use the same kernel')
configured = loaded[configure.name]
for report in loaded.values():
    if not report.get('native_4k_mmu_observed') or not report.get('crypto14_initialization_observed'):
        raise SystemExit('Native 4K and real crypto initialization must precede platform matching')
if int(configured['x0'], 16) != 1 or configured['pc'] != configured.get('function_return_target'):
    raise SystemExit('ArmDTPlatform::configure did not return success to its actual caller')
globals_ = configured.get('armdt_globals', {})
expected = {
    '_armdt_platform_configured': 1,
    '_armdt_platform_cpu_count': 1,
    '_armdt_platform_bus_count': 1,
    '_armdt_platform_defaults_count': 1,
    '_armdt_platform_nvram_proxy': 1,
}
for name, value in expected.items():
    if globals_.get(name) != value:
        raise SystemExit(f'{name} is {globals_.get(name)!r}, expected {value}')
if globals_.get('_armdt_platform_child_count', 0) < 8:
    raise SystemExit('The real top-level device tree was not published')
if globals_.get('_armdt_platform_device_count', 0) < 1:
    raise SystemExit('No arm-io device nub was published')

if not args.configure_only:
    late = loaded[bsd.name]
    if late.get('stop_symbol') != '_bsd_init':
        raise SystemExit(f"The next real boundary is {late.get('stop_symbol')!r}, not bsd_init")
    if late.get('armdt_globals') != globals_:
        raise SystemExit('Platform counters changed before bsd_init')
    native_ufs = late.get('native_ufs')
    if not native_ufs or native_ufs.get('probe_calls', 0) < 1:
        raise SystemExit(f'NativeUfs personality never probed a platform device: {native_ufs!r}')
    if native_ufs.get('mapped') != 0 or native_ufs.get('probe_requested') != 0:
        raise SystemExit('NativeUfs touched UFS MMIO without the explicit probe argument')
    # The UFS-specific compatible match is not yet asserted: at this breakpoint
    # IOKit may still be matching the published arm-io children. The safe
    # property proven here is probe invocation with no MMIO by default.

if not args.configure_only:
    native_ufs = late.get('native_ufs') or {}
else:
    native_ufs = configured.get('native_ufs') or {}
result = {
    'kernel_sha256': hashes.pop(),
    'platform_configure_returned_true': True,
    'cpu_nubs': 1,
    'bus_nubs': 1,
    'defaults_nubs': globals_['_armdt_platform_defaults_count'],
    'nvram_proxy_published': True,
    'total_children': globals_['_armdt_platform_child_count'],
    'bus_device_nubs': globals_['_armdt_platform_device_count'],
    'bsd_init_observed': not args.configure_only,
    'native_4k_observed': True,
    'native_ufs_probe_calls': native_ufs['probe_calls'],
    'native_ufs_matched_in_adt': native_ufs.get('matched', 0) == 1,
    'native_ufs_mmio_default_off': True,
    'qemu_only': True,
    'sheng_hardware_tested': False,
    'cpu_interrupt_delivery_proven': False,
    'ipados_userspace_boot_demonstrated': False,
}
output = ROOT / 'build/armdt-platform'
output.mkdir(parents=True, exist_ok=True)
(output / 'test-report.json').write_text(json.dumps(result, indent=2) + '\n')
print('PASS: real DT platform services, CPU nub and NVRAM proxy; native 4K retained'
      + ('; bsd_init reached' if not args.configure_only else ''))
