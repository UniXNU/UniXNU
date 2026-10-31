#!/usr/bin/env python3
"""Check unpublished original provider lifetime and its real first required callback."""
import argparse,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kits/XnuPrelink'))
from native_prelink import macho,backed_offset,exports

def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,why):
 if not ok:raise SystemExit(why)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate-base',type=Path,default=ROOT/'build/xnu-prelink/native-owner-original-descriptor-refusal-candidate');args=p.parse_args()
base=args.candidate_base.resolve();plan=load(base.with_suffix('.json'));raw=base.with_suffix('.macho').read_bytes();segments=macho(raw)['segments']
require(sha(base.with_suffix('.macho'))==plan['candidate_sha256'] and sha(ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')==plan['native_sha256'],'Exact current native kernel/candidate')
reference=load(ROOT/'build/xnu-prelink/native-owner-metal-shared-events-candidate.json');require(plan['components']==reference['components'] and plan['original_executable_sha256']==reference['original_executable_sha256'] and plan['early_security_initializers']==reference['early_security_initializers'],'Same 29 unchanged original components/security entry')
for module,digest in plan['original_executable_sha256'].items():
 e=next(e for e in plan['extents'] if e['module']==module and e['segment']=='__TEXT_EXEC');o=backed_offset(segments,e['va'],e['size'],len(raw));require(hashlib.sha256(raw[o:o+e['size']]).hexdigest()==digest,'Actual whole original executable identity '+module)
build=load(ROOT/'build/native-original-provider/build-report.json');broker_build=load(ROOT/'build/native-offline-gpu/build-report.json');abi=load(ROOT/'build/gpu-analysis/original-iogpu-provider-abi.json')
for manifest in (build['source_sha256'],broker_build['source_sha256']):
 for rel,digest in manifest.items():require(sha(ROOT/rel)==digest,'Exact compiled own source '+rel)
require(sha(ROOT/'build/native-original-provider/libNativeIOGPUProviderProbe.late.a')==build['archive_sha256'] and sha(ROOT/'build/native-offline-gpu/libNativeOfflineGPU.late.a')==broker_build['archive_sha256'] and sha(ROOT/'build/gpu-analysis/original-iogpu-provider-abi.json')==build['abi_sha256'],'Actual compiled archives and original ABI inputs')
reports=[]
for suffix in ('','-start','-missing-base','-default-off'):
 fixture=ROOT/('build/darwinboot-owner-hvf-original-provider-start' if suffix=='-start' else 'build/darwinboot-owner-hvf-original-provider-abi'+suffix);d=load(fixture/'gdb-stop.json');sink=load(fixture/'console-sink.json')
 require(d['kernel_sha256']==plan['candidate_sha256'] and not d['bounded_timeout_interrupted'] and d['qemu_accelerator']=='hvf' and d['native_4k_mmu_observed'] and not d['sheng_hardware_tested'],'Actual bounded new native-4K kernel observation')
 r={k:int(v,16) for k,v in d['system_registers'].items()};require((r['TCR_EL1']>>14)&3==0 and (r['TCR_EL1']>>30)&3==2 and r['SCTLR_EL1']&1 and r['TTBR0_EL1'] and r['TTBR1_EL1'],'Actual active CPU TCR/TTBR/SCTLR, independent of GPU SMMU')
 require(sink['protocol_responses_sent']==0 and 0<=sink['bytes_observed']<=65536 and not sink['errors'] and not sink['gpu_execution'] and not sink['system_device_published'],'Bounded firmware console prefix receives zero protocol responses; no GPU execution/publication')
 console=d['native_console_globals'];require(all(console['_native_console_'+name]==0 for name in ('tx_requests','rx_requests','failures','tx_bytes','rx_bytes')),'Actual kernel transport sends/receives no GPU protocol bytes after the independent firmware prefix')
 require(d['original_crypto_initialized_observed'] and d['original_crypto_table_owner_observed'],'Actual unchanged original crypto initialization')
 b=d['native_gpu_broker'];require(not b['clients'] and not b['requests'] and not b['actual_cpu_contexts'] and not any(d['native_gpu_shared_events'].values()),'No actual GPU userclient, command or shared capability opened')
 if suffix!='-default-off':require(d['stop_symbol']=='_native_original_provider_checkpoint' and b['stage']==3 and not b['status'],'Actual early private hook boundary, not an OS/desktop boot')
 reports.append(d)
positive,started,missing,off=reports
p=positive['native_original_provider'];t=started['native_original_provider'];m=missing['native_original_provider'];z=off['native_original_provider']
names={name:address for address,group in exports(raw,macho(raw)).items() for name in group}
def table(address,count):
 o=backed_offset(segments,address,count*8,len(raw));return struct.unpack_from('<'+'Q'*count,raw,o)
original=table(abi['vptr'],215)
reference_raw=(ROOT/'build/xnu-prelink/native-owner-renderbox-presentation-candidate.macho').read_bytes()
reference_exports=exports(reference_raw,macho(reference_raw))
expected=[]
for address in abi['inherited_entries']:
 aliases=reference_exports.get(address,[])
 relocated={names[name] for name in aliases if name in names}
 require(len(relocated)<=1,'Unambiguous native inherited export relocation')
 expected.append(next(iter(relocated)) if relocated else address)
require(list(original)==expected,'Whole original table preserves original implementations with exact new native export relocation')
for obj in (p,t):
 require(obj['parent']==abi['metaclass'] and obj['size']==736 and obj['allocated']==obj['initialized']==obj['parent_match']==1 and obj['object'] and obj['backend'],'Actual own object has genuine original parent and storage extent')
 require(not obj['attached'] and not obj['registered'] and not obj['start_returned'] and not obj['start_result'],'No attachment, publication or successful original startup')
 require(obj['instances_live']==obj['instances_before']+1,'Actual own instance count increases')
 actual=table(obj['vptr'],215)
 require([i for i,(a,b) in enumerate(zip(original,actual)) if a!=b]==build['own_entries'],'Only own metadata, nonreturning required hooks and publication guard differ')
 for slot in (14,81,82,86,87,111,141):require(actual[slot]==original[slot],'Actual operational slot still targets original code '+str(slot))
require(p['stage']==3 and not p['status'] and p['released']==1 and p['instances_after']==p['instances_before'] and not p['callback'] and not any(p['frame']),'Original C2/init/free/D2 restores actual instance count with no required hook')
require(t['stage']==4 and t['status']==0xe00002c7-(1<<32) and t['callback']==195 and not t['released'] and not t['instances_after'],'Real original start intentionally stops at first unimplemented required hook; no cleanup or successful return claimed')
f=t['frame'];require(f[0]==t['object'] and f[1]==t['backend'] and f[9]==abi['first_required_dispatch']['pc']+20,'Actual this/provider registers and caller LR come from the exact original start call site')
require((f[10]>>14)&3==0 and (f[10]>>30)&3==2 and f[11]&1 and f[12] and f[13] and f[14]%16==0,'Naked required hook captures actual native CPU 4K translation and aligned original SP')
require(m['stage']==1 and m['status']==0xe00002f0-(1<<32) and not m['parent'] and not m['allocated'] and not m['initialized'] and not m['released'],'Missing original class returns real kIOReturnNotFound before own registration/allocation')
require(z['stage']==0 and z['status']==-1 and all(not any(value) if isinstance(value,list) else not value for key,value in z.items() if key!='status') and off['stop_symbol']=='original-launchd-main' and off['original_launchd_main_executed'] and off['followed_main_entry']['first_instruction_completed'] and off['owner_root_binding_audit']['boot_root_accepted'] and off['original_amfi_table_owner_observed'] and off['actual_signature_failures']==dict(_cs_validate_page_bad_hash=0,_cs_validate_page_no_hash=0) and off['direct_user_commpage_shifts']=={'fffff4025:1':12,'fffff4037:1':12},'Default-off actually executes unchanged original launchd/root/AMFI/native4K userspace with zero provider allocation')
result=dict(candidate_sha256=plan['candidate_sha256'],native_sha256=plan['native_sha256'],actual_original_protected_constructor_destructor=True,actual_original_init_free=True,lifecycle_instance_count_restored=True,actual_original_start_entered=True,actual_first_required_slot=195,actual_this_provider_and_caller=True,required_callback_implemented=False,start_successful=False,start_object_released=False,normal_system_device_published=False,normal_system_authorization=False,actual_gpu_execution=False,original_desktop=False,active_native_adreno_4k=False,reports_sha256={name:sha(ROOT/'build'/name/'gdb-stop.json') for name in ('darwinboot-owner-hvf-original-provider-abi','darwinboot-owner-hvf-original-provider-start','darwinboot-owner-hvf-original-provider-abi-missing-base','darwinboot-owner-hvf-original-provider-abi-default-off')})
(ROOT/'build/native-original-provider/runtime-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: original C2/init/free/D2 lifetime; actual original start reaches required slot195 with real this/provider/LR; missing/default-off controls')
print('The required hook deliberately does not return. No successful startup, publication, GPU execution, active Adreno SMMU or desktop is qualified')
