#!/usr/bin/env python3
"""Qualify actual original RenderBox queue queries up to its next real refusal."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct
import subprocess
import sys
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--enqueue',action='store_true');p.add_argument('--texture-refusal',action='store_true');p.add_argument('--private-texture-refusal',action='store_true');p.add_argument('--stencil-texture-refusal',action='store_true');a=p.parse_args()
if a.stencil_texture_refusal:a.private_texture_refusal=True
if a.private_texture_refusal:a.texture_refusal=True
if a.texture_refusal:a.enqueue=True
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(value,message):
    if not value:raise SystemExit(message)
subprocess.run(['python3',ROOT/'scripts/audit-target-renderbox-device.py'],check=True,timeout=60,capture_output=True)
sys.path.insert(0,str(ROOT/'kits/XnuPrelink'));from native_prelink import macho,backed_offset
kernel=ROOT/('build/xnu-prelink/native-owner-offline-gpu-texture-copy-candidate.macho' if a.stencil_texture_refusal else 'build/xnu-prelink/native-owner-offline-gpu-enqueue-candidate.macho' if a.enqueue else 'build/xnu-prelink/native-owner-offline-gpu-priority-candidate.macho');plan=load(kernel.with_suffix('.json'));raw=kernel.read_bytes();image=macho(raw)
require(sha(kernel)==plan['candidate_sha256'] and sha(ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')==plan['native_sha256'],'Exact current native kernel and original-component candidate')
for module,digest in plan['original_executable_sha256'].items():
    e=next(e for e in plan['extents'] if e['module']==module and e['segment']=='__TEXT_EXEC');at=backed_offset(image['segments'],e['va'],e['size'],len(raw))
    require(hashlib.sha256(raw[at:at+e['size']]).hexdigest()==digest,'Whole original executable remains unchanged '+module)
folder=ROOT/'build/offline-renderbox-draw';build=load(folder/'build-report.json');data=load(folder/'data-report.json')
require(sha(folder/'air-native')==build['process_sha256']==data['process_sha256'] and sha(folder/'test-inputs.json')==build['manifest_sha256']==data['manifest_sha256'] and
    sha(folder/'compiler-data-32.cdr')==data['sha256'] and sha(folder/'offline-trust.bundle')==build['trust_bundle_sha256'] and
    sha(folder/'NativeOfflineMetal.bundle/NativeOfflineMetal')==build['plugin_sha256'],'Exact own drawing process, bundle, Data, manifest and trust')
for name,digest in load(folder/'test-inputs.json')['sources'].items():require(sha(ROOT/name)==digest,'Exact executed source '+name)
for path in (folder/'air-native',folder/'NativeOfflineMetal.bundle'):
    subprocess.run(['codesign','--verify','--strict',path],check=True,timeout=30,capture_output=True)
report=ROOT/'build/darwinboot-owner-hvf-offline-renderbox-draw-cpu-contexts/gdb-stop.json';d=load(report)
require(d['kernel_sha256']==plan['candidate_sha256'] and not d['bounded_timeout_interrupted'] and d['stop_symbol']=='_exception_triage' and
    d['native_4k_mmu_observed'] and d['original_amfi_table_owner_observed'] and d['owner_root_binding_audit']['boot_root_accepted'] and
    d['actual_signature_failures']==dict(_cs_validate_page_bad_hash=0,_cs_validate_page_no_hash=0) and
    d['scratch_data']['actual_seed_sha256']==data['sha256'] and d['trust_cache_bundle_sha256']==build['trust_bundle_sha256'],
    'Actual original runtime, native CPU 4K, original AMFI and authenticated root')
u=d['entry_user_state_candidates'][0];v=struct.unpack('<32Q',bytes.fromhex(u['register_memory']['13:100']['bytes']))
reason=bytes.fromhex(u['register_memory']['14:200']['bytes']).split(b'\0')[0].decode()
require(u['pointer']==d['actual_process']['user_state'] and int(u['cpsr'],16)&31==0 and u['instruction_bytes'].startswith('000020d4') and
    v[:6]==(0x52424641,d['actual_process']['pid'],4096,4096,70 if a.texture_refusal else 64,24) and
    (reason==('Actual own texture refusal type 2 format 253 extent 64x64 depth 1 levels 1 samples 1 array 1 usage 4 storage 2 cache 0 hazard 0 optimized 1 surface 0 format 0 planes 0 plane 0' if a.stencil_texture_refusal else 'Actual own texture refusal type 2 format 65 extent 64x64 depth 1 levels 1 samples 1 array 1 usage 4 storage 2 cache 0 hazard 0 optimized 1 surface 0 format 0 planes 0 plane 0' if a.private_texture_refusal else 'Actual own texture refusal type 2 format 70 extent 64x64 depth 1 levels 1 samples 1 array 1 usage 5 storage 0 cache 0 hazard 0 optimized 1 surface 1 format 1380401729 planes 0 plane 0') if a.texture_refusal else reason.startswith('Actual uncaught NSInvalidArgumentException: -[OMCommandObject '+('addCompletedHandler:' if a.enqueue else 'enqueue')+']: unrecognized selector sent to instance ')),
    'Actual original RenderBox has advanced past priority queries to the next genuine resource/submission boundary')
broker=d['native_gpu_broker'];rows=broker['actual_cpu_contexts'];require(len(rows)==2 and len({r['task'] for r in rows})==len({r['TTBR0_EL1'] for r in rows})==2,'Two actual independent worker CPU contexts')
for r in rows:
    tcr=int(r['TCR_EL1'],16);require(tcr>>14&3==0 and tcr>>30&3==2 and int(r['SCTLR_EL1'],16)&1 and int(r['TTBR0_EL1'],16) and int(r['TTBR1_EL1'],16) and r['native_cpu_4k_accepted'],'Actual worker MMU/TTBR/native-4K state')
host=load(folder/'host-cpu-contexts-report.json');priorities=host['queue_priorities'];ops=host['operations']
require(not host['transport_healthy'] and not host['session_finished'] and not host['completed_commands'] and
    not host['cpu_pixel_renderer'] and not host['original_desktop'] and not host['adreno_execution'] and
    len(ops)==broker['requests']==(32 if a.stencil_texture_refusal else 30 if a.private_texture_refusal else 16 if a.enqueue else 14) and broker['reply_bytes']==(1376 if a.stencil_texture_refusal else 1312 if a.private_texture_refusal else 864 if a.enqueue else 784) and not broker['failures'] and broker['refusals']==(2 if a.private_texture_refusal else 0) and
    all(o['request']==i+1 for i,o in enumerate(ops)) and sum(bool(o['error']) for o in ops)==(2 if a.private_texture_refusal else 0) and all(o['operation']==0x104 and o['error']==-4 for o in ops if o['error']),
    'Exact incomplete real GPU ledger, with no invented frame, completion or successful close')
require(len(priorities)==4 and {p['session'] for p in priorities}=={r['session'] for r in rows} and
    all(not p['writing'] and p['before']==p['after']==p['result']==(2 if p['background'] else 1) for p in priorities) and
    len({p['queue'] for p in priorities})==2 and all({p['background'] for p in priorities if p['session']==r['session']}=={0,1} for r in rows),
    'Both original RenderBox workers query actual distinct foreground/background GPU priorities')
if a.private_texture_refusal:
    textures=[o for o in ops if o['operation']==0x104 and not o['error']]
    require(len(textures)==(4 if a.stencil_texture_refusal else 2) and {o['session'] for o in textures}=={r['session'] for r in rows} and
        len(host['texture_uploads'])==10 and sum(r['bytes'] for r in host['texture_uploads'])==32768,
        'Both original RGBA IOSurface textures genuinely allocate and upload before the next private RG16Float request refuses')
if a.enqueue:
    enqueued=host['enqueued_commands'];require(len(enqueued)==host['pending_enqueues']==2 and
        {r['session'] for r in enqueued}=={r['session'] for r in rows} and all(r['status']==1 for r in enqueued) and
        all(ops[r['operation_request']-1]['operation']==0x121 and not ops[r['operation_request']-1]['error'] for r in enqueued),
        'Both original RenderBox command buffers are really Enqueued, still pending and never reported Completed')
for name,digest in load(ROOT/'build/host-metal/qualification.json')['backend_sources'].items():require(sha(ROOT/name)==digest,'Exact actual host backend '+name)
(ROOT/('build/native-offline-gpu/renderbox-stencil-texture-refusal.json' if a.stencil_texture_refusal else 'build/native-offline-gpu/renderbox-private-texture-refusal.json' if a.private_texture_refusal else 'build/native-offline-gpu/renderbox-texture-refusal.json' if a.texture_refusal else 'build/native-offline-gpu/renderbox-enqueue.json' if a.enqueue else 'build/native-offline-gpu/renderbox-queue-priority.json')).write_text(json.dumps(dict(candidate_sha256=sha(kernel),native_sha256=plan['native_sha256'],
    report_sha256=sha(report),host_report_sha256=sha(folder/'host-cpu-contexts-report.json'),actual_priority_queries=4,actual_enqueued_commands=2 if a.enqueue else 0,actual_native_cpu_4k_workers=2,
    next_refusal=reason,original_renderbox_frame=False,original_desktop=False,adreno_execution=False,active_native_adreno_4k=False),indent=2)+'\n')
if a.stencil_texture_refusal:print('PASS: original RenderBox RGBA and private RG16Float textures allocate; next actual Stencil8 request refuses before CPU fallback')
elif a.private_texture_refusal:print('PASS: original RenderBox RGBA IOSurfaces allocate; next actual private RG16Float texture refuses before CPU fallback, without a GPU frame claim')
elif a.texture_refusal:print('PASS: actual original RenderBox RGBA8/RGBA IOSurface request refuses in the own frontend before any CPU fallback; no GPU frame claimed')
else:print('PASS: original RenderBox priority queries'+(' and actual GPU command enqueue' if a.enqueue else '')+' reach the native-4K broker; the next genuine refusal remains explicit')
