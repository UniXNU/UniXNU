#!/usr/bin/env python3
"""Qualify actual original-base construction/lifetime and two real unpublished controls."""
import hashlib,json,re,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kits/XnuPrelink'))
from native_prelink import macho,backed_offset,exports
def require(v,s):
 if not v:raise SystemExit(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
base=ROOT/'build/xnu-prelink/native-owner-accelerator-abi-candidate';plan=load(base.with_suffix('.json'));raw=base.with_suffix('.macho').read_bytes();im=macho(raw)
require(hashlib.sha256(raw).hexdigest()==plan['candidate_sha256'] and sha(ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')==plan['native_sha256'],'Exact current native and immutable candidate')
old=load(ROOT/'build/xnu-prelink/native-owner-offline-gpu-broker-cpu-candidate.json')
require(plan['components']==old['components'] and plan['original_executable_sha256']==old['original_executable_sha256'] and plan['early_security_initializers']==old['early_security_initializers'],'Same original component/security initialization closure')
for module,digest in plan['original_executable_sha256'].items():
 e=next(e for e in plan['extents'] if e['module']==module and e['segment']=='__TEXT_EXEC');at=backed_offset(im['segments'],e['va'],e['size'],len(raw))
 require(hashlib.sha256(raw[at:at+e['size']]).hexdigest()==digest,'Complete unchanged original executable: '+module)
abi=load(ROOT/'build/gpu-analysis/ioaccelerator-base-abi.json');build=load(ROOT/'build/native-offline-accelerator/build-report.json');broker=load(ROOT/'build/native-offline-gpu/build-report.json')
for report in (build,broker):
 for name,digest in report['source_sha256'].items():require(sha(ROOT/name)==digest,'Exact actual compiled source: '+name)
require(broker['accelerator_abi_probe'] and sha(ROOT/'build/native-offline-gpu/libNativeOfflineGPU.late.a')==broker['archive_sha256'] and
 sha(ROOT/'build/native-offline-accelerator/libNativeOfflineAccelerator.late.a')==build['archive_sha256'] and
 build['original_abi_sha256']==sha(ROOT/'build/gpu-analysis/ioaccelerator-base-abi.json') and build['virtual_entries']==168 and build['owned_entries']==[0,1,7],
 'Actual explicitly enabled component, inherited table and exactly qualified original constructor/destructor/meta imports')
names={n:v for v,group in exports(raw,im).items() for n in group};vtable=names['__ZTV24NativeOfflineAccelerator']+16
records=[]
for case in ('positive','missing-base','default-off'):
 folder=ROOT/'build'/('darwinboot-owner-hvf-accelerator-abi'+('' if case=='positive' else '-'+case));path=folder/'gdb-stop.json';d=load(path);state=d['native_accelerator']
 require(d['kernel_sha256']==plan['candidate_sha256'] and not d['bounded_timeout_interrupted'] and
 d['stop_symbol']==('_native_gpu_broker_checkpoint' if case=='default-off' else '_native_accelerator_checkpoint') and d['native_4k_mmu_observed'] and
 d['original_amfi_table_owner_observed'] and d['actual_signature_failures']==dict(_cs_validate_page_bad_hash=0,_cs_validate_page_no_hash=0),
 'Actual bounded native CPU-4K/original AMFI kernel observation, not a userspace/desktop checkpoint')
 require(not d['owner_root_binding_audit']['boot_root_accepted'],'These actual early observations precede root acceptance; never report them as a root/userspace boot')
 require(d['native_iogpu_load_status']==(-1 if case=='missing-base' else 0),'Actual original IOGPU component load/default-off state')
 if case=='positive':
  require(state['stage']==3 and not state['status'] and state['allocated']==state['initialized']==state['parent_match']==state['released']==1 and
   not state['unrelated_match'] and not state['attached'] and state['size']==136 and state['instances_before']==state['instances_after']==0 and state['instances_live']==1 and
   state['object'] and state['vptr']==vtable and state['parent']==state['superclass']==int(abi['metaclass'],16),
   'Real original C2-backed object initializes, matches its actual original parent, stays outside registry planes and releases its only live instance')
 else:
  require(state['stage']==(1 if case=='missing-base' else 0) and state['status']==(-536870160 if case=='missing-base' else -1) and
   all(not value for name,value in state.items() if name not in ('stage','status')),
   'Actual missing original parent refuses before allocation; default-off constructs no object or device')
 b=d['native_gpu_broker'];require(b['stage']==3 and not b['status'] and all(not b[name] for name in ('clients','active','closed','requests','failures','refusals','reply_bytes')) and not b['actual_cpu_contexts'],
  'Only the unchanged private service startup occurs; no GPU clients, submissions or protocol success is invented')
 sink=load(folder/'console-sink.json');require(not sink['errors'] and sink['protocol_responses_sent']==0 and not sink['gpu_execution'] and not sink['system_device_published'],'Read-only console prefix sink supplies zero GPU replies')
 records.append(dict(case=case,report_sha256=sha(path),actual_class_state=state,original_root_accepted=False,userspace_executed=False))
(ROOT/'build/native-offline-accelerator/abi-checkpoint.json').write_text(json.dumps(dict(candidate_sha256=plan['candidate_sha256'],native_sha256=plan['native_sha256'],observations=records,
 actual_original_base_lifecycle=True,actual_instance_counts=[0,1,0],actual_native_cpu_4k=True,original_instructions_modified=False,
 system_device_published=False,system_metal=False,original_desktop=False,adreno_execution=False,active_native_adreno_4k=False),indent=2)+'\n')
print('PASS: real original IOAcceleratorES constructor/ancestry/lifetime (0 -> 1 -> 0), actual missing-parent refusal and default-off; no device attached/published')
print('Early native CPU 4K/kernel ABI evidence only, before root acceptance/userland; normal Metal, desktop and Adreno remain open')
