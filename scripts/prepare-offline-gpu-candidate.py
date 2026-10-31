#!/usr/bin/env python3
"""Emit a fresh immutable offline candidate with exactly the retained original components."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
base=ROOT/'build/xnu-prelink/native-owner-offline-gpu-broker-cpu-candidate.json';old=json.loads(base.read_text())
kernel=ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped'
original=ROOT/'.cache/firmware/kernelcache.macho/kernelcache.release.ipad7.decompressed';output=a.output.resolve()
if output.exists() or output.with_suffix('.json').exists():raise SystemExit('Refuse to overwrite any existing candidate or report')
if sha(original)!=old['original_sha256'] or sha(base.with_suffix('.macho'))!=old['candidate_sha256']:raise SystemExit('Exact original target and retained base candidate required')
cmd=['python3',ROOT/'kits/XnuPrelink/emit_prelink.py','--kernel',kernel,'--prelinked',original,'--slide='+hex(old['slide']),'--output',output]
for root in old['components']:cmd+=['--root',root]
# The emitted plan records relocated addresses; the emitter consumes ORIGINAL VAs.
for name,address in old['early_security_initializers'].items():cmd+=['--early-security-init',name+'='+hex(address-old['slide'])]
subprocess.run([str(v) for v in cmd],check=True,timeout=180)
new=json.loads(output.with_suffix('.json').read_text())
if new['components']!=old['components'] or new['original_executable_sha256']!=old['original_executable_sha256'] or new['early_security_initializers']!=old['early_security_initializers']:
    raise SystemExit('Original component set/code/security initialization changed')
if sha(output)!=new['candidate_sha256'] or sha(kernel)!=new['native_sha256']:raise SystemExit('Candidate/native identity differs')
print('PASS: fresh immutable candidate, same 29 unchanged original executable components and real early-security entry; runtime remains unqualified')
print('Candidate SHA-256:',new['candidate_sha256']);print('Native SHA-256:',new['native_sha256'])
