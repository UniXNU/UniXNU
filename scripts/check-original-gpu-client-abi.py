#!/usr/bin/env python3
"""Check genuine original userclient lifecycle/refusal without a publication claim."""
import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kits/XnuPrelink'))
from native_prelink import macho,backed_offset,exports

def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,why):
 if not ok:raise SystemExit(why)
base=ROOT/'build/xnu-prelink/native-owner-original-client-abi-candidate';plan=load(base.with_suffix('.json'));raw=base.with_suffix('.macho').read_bytes();segments=macho(raw)['segments']
require(sha(base.with_suffix('.macho'))==plan['candidate_sha256'] and sha(ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')==plan['native_sha256'],'Exact current native kernel/candidate')
reference=load(ROOT/'build/xnu-prelink/native-owner-metal-shared-events-candidate.json');require(plan['components']==reference['components'] and plan['original_executable_sha256']==reference['original_executable_sha256'] and plan['early_security_initializers']==reference['early_security_initializers'],'Same 29 unchanged original components/security entry')
for module,digest in plan['original_executable_sha256'].items():
 e=next(e for e in plan['extents'] if e['module']==module and e['segment']=='__TEXT_EXEC');o=backed_offset(segments,e['va'],e['size'],len(raw));require(hashlib.sha256(raw[o:o+e['size']]).hexdigest()==digest,'Actual whole original executable identity '+module)
build=load(ROOT/'build/native-offline-accelerator/build-report.json');broker_build=load(ROOT/'build/native-offline-gpu/build-report.json');abi=load(ROOT/'build/gpu-analysis/original-iogpu-userclient-abi.json')
for manifest in (build['source_sha256'],broker_build['source_sha256']):
 for rel,digest in manifest.items():require(sha(ROOT/rel)==digest,'Exact compiled own source '+rel)
require(sha(ROOT/'build/native-offline-accelerator/libNativeOfflineAccelerator.late.a')==build['archive_sha256'] and sha(ROOT/'build/native-offline-gpu/libNativeOfflineGPU.late.a')==broker_build['archive_sha256'] and sha(ROOT/'build/gpu-analysis/original-iogpu-userclient-abi.json')==build['original_client_abi_sha256'],'Actual compiled archives and original ABI inputs')
reports=[]
for suffix in ('','-missing-base','-default-off'):
 fixture=ROOT/('build/darwinboot-owner-hvf-original-client-abi'+suffix);d=load(fixture/'gdb-stop.json');sink=load(fixture/'console-sink.json')
 require(d['kernel_sha256']==plan['candidate_sha256'] and not d['bounded_timeout_interrupted'] and d['qemu_accelerator']=='hvf' and d['native_4k_mmu_observed'] and not d['sheng_hardware_tested'],'Actual bounded new native-4K kernel observation')
 r={k:int(v,16) for k,v in d['system_registers'].items()};require((r['TCR_EL1']>>14)&3==0 and (r['TCR_EL1']>>30)&3==2 and r['SCTLR_EL1']&1 and r['TTBR0_EL1'] and r['TTBR1_EL1'],'Actual active CPU TCR/TTBR/SCTLR, independent of GPU SMMU')
 require(sink['protocol_responses_sent']==0 and 0<=sink['bytes_observed']<=65536 and not sink['errors'] and not sink['gpu_execution'] and not sink['system_device_published'],'Bounded firmware console prefix receives zero protocol responses; no GPU execution/publication')
 console=d['native_console_globals'];require(all(console['_native_console_'+name]==0 for name in ('tx_requests','rx_requests','failures','tx_bytes','rx_bytes')),'Actual kernel transport sends/receives no GPU protocol bytes after the independent firmware prefix')
 require(d['original_crypto_initialized_observed'] and d['original_crypto_table_owner_observed'],'Actual unchanged original crypto initialization')
 b=d['native_gpu_broker'];require(not b['clients'] and not b['requests'] and not b['actual_cpu_contexts'] and not any(d['native_gpu_shared_events'].values()),'No actual GPU userclient, command or shared capability opened')
 if suffix!='-default-off':require(d['stop_symbol']=='_native_original_client_checkpoint' and b['stage']==3 and not b['status'],'Actual early private hook boundary, not an OS/desktop boot')
 reports.append(d)
positive,missing,off=reports;p=positive['native_original_client'];m=missing['native_original_client'];z=off['native_original_client']
names={name:address for address,group in exports(raw,macho(raw)).items() for name in group}
require(p['parent']==names['__ZN12IOUserClient10gMetaClassE'],'Actual live parent is this new kernel original native IOUserClient metaclass')
def table(address,count):
 o=backed_offset(segments,address,count*8,len(raw));return struct.unpack_from('<'+'Q'*count,raw,o)
base_table=table(names['__ZTV12IOUserClient']+16,186);actual_table=table(p['vptr'],189)
require([i for i,(a,b) in enumerate(zip(base_table,actual_table)) if a!=b]==[0,1,7,14,86,87,168,169,172,185] and actual_table[14]==int(abi['free'],16) and actual_table[86]==int(abi['start'],16),'Observed real object uses untouched original operational methods and the actual new native ABI prefix')
require(p['stage']==3 and not p['status'] and p['allocated']==p['initialized']==p['parent_match']==p['released']==p['provider_initialized']==1 and not p['unrelated_match'] and not p['attached'] and not p['wrong_start'] and p['size']==304 and p['parent_size']==216 and p['object'] and p['meta']==int(abi['metaclass'],16) and p['vptr']==int(abi['vptr'],16),'Real original concrete class C2/initialization, genuine ancestry and wrong-provider start refusal, without any attachment')
require(p['instances_live']==p['instances_before']+1 and p['instances_after']==p['instances_before'],'Actual original instance count rises/falls through original free/D2')
require(m['stage']==1 and m['status']==0xe00002f0-(1<<32) and not m['meta'] and not m['allocated'] and not m['initialized'] and not m['released'],'Original class absent genuinely refuses with native kIOReturnNotFound before allocation')
require(z['stage']==0 and z['status']==-1 and all(not value for key,value in z.items() if key!='status') and off['stop_symbol']=='original-launchd-main' and off['original_launchd_main_executed'] and off['followed_main_entry']['first_instruction_completed'] and off['owner_root_binding_audit']['boot_root_accepted'] and off['original_amfi_table_owner_observed'] and off['actual_signature_failures']==dict(_cs_validate_page_bad_hash=0,_cs_validate_page_no_hash=0) and off['direct_user_commpage_shifts']=={'fffff4025:1':12,'fffff4037:1':12},'Default-off new kernel genuinely executes unchanged original launchd main/root/AMFI/native-4K ABI with no original-client allocation')
(ROOT/'build/native-offline-accelerator/original-client-checkpoint.json').write_text(json.dumps(dict(candidate_sha256=plan['candidate_sha256'],native_sha256=plan['native_sha256'],actual_original_userclient_instance=True,actual_original_init_and_free=True,wrong_provider_start_refused=True,instance_count_restored=True,positive_report_sha256=sha(ROOT/'build/darwinboot-owner-hvf-original-client-abi/gdb-stop.json'),missing_report_sha256=sha(ROOT/'build/darwinboot-owner-hvf-original-client-abi-missing-base/gdb-stop.json'),default_off_report_sha256=sha(ROOT/'build/darwinboot-owner-hvf-original-client-abi-default-off/gdb-stop.json'),no_original_client_published=True,normal_system_authorization=False,actual_gpu_execution=False,original_desktop=False,active_native_adreno_4k=False),indent=2)+'\n')
print('PASS: genuine original IOGPU userclient C2/init/free, real wrong-provider refusal and restored instance count; missing/default-off controls pass')
print('No operational client/provider, normal system authorization, GPU execution or original desktop is qualified')
