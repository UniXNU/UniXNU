#!/usr/bin/env python3
"""Qualify original QuartzCore vertex inputs in two real native 4K GPU workers."""
import argparse,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'kits/XnuPrelink'))
from native_prelink import macho,backed_offset
def require(value,why):
 if not value:raise SystemExit(why)
def load(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def modules(raw):
 n=struct.unpack_from('<I',raw)[0];starts=struct.unpack_from('<'+'I'*n,raw,4)
 return [raw[a:b] for a,b in zip(starts,(*starts[1:],len(raw)))]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate-base',type=Path,default=ROOT/'build/xnu-prelink/native-owner-original-provider-probe-candidate');a=p.parse_args()
folder=ROOT/'build/offline-metal-vertex-inputs';fixture=ROOT/'build/darwinboot-owner-hvf-offline-metal-vertex-inputs'
d=load(fixture/'gdb-stop.json');host=load(folder/'host-enabled-report.json');provenance=load(folder/'host-enabled-provenance.json')
build=load(folder/'build-report.json');data=load(folder/'data-report.json');manifest=load(folder/'test-inputs.json')
base=a.candidate_base.resolve();plan=load(base.with_suffix('.json'));raw=base.with_suffix('.macho').read_bytes();segments=macho(raw)['segments']
require(sha(base.with_suffix('.macho'))==plan['candidate_sha256']==d['kernel_sha256'],'Actual immutable candidate identity')
require(sha(ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')==plan['native_sha256'],'Exact current native kernel')
broker_build=load(ROOT/'build/native-offline-gpu/build-report.json')
for rel,digest in broker_build['source_sha256'].items():require(sha(ROOT/rel)==digest,'Exact compiled native broker source: '+rel)
require(sha(ROOT/'build/native-offline-gpu/libNativeOfflineGPU.late.a')==broker_build['archive_sha256'],'Exact compiled private broker archive')
old=load(ROOT/'build/xnu-prelink/native-owner-offline-gpu-broker-cpu-candidate.json')
require(plan['components']==old['components'] and plan['original_executable_sha256']==old['original_executable_sha256'] and plan['early_security_initializers']==old['early_security_initializers'],'All 29 original executable hashes and security initialization preserved')
for module,digest in plan['original_executable_sha256'].items():
 e=next(e for e in plan['extents'] if e['module']==module and e['segment']=='__TEXT_EXEC');at=backed_offset(segments,e['va'],e['size'],len(raw))
 require(hashlib.sha256(raw[at:at+e['size']]).hexdigest()==digest,'Actual whole original executable identity: '+module)
for name,digest in manifest['sources'].items():require(sha(ROOT/name)==digest,'Exact compiled frontend/instrument source: '+name)
require(sha(folder/'air-native')==build['process_sha256']==data['process_sha256'] and sha(folder/'compiler-data-32.cdr')==data['sha256'] and
 sha(folder/'test-inputs.json')==build['manifest_sha256']==data['manifest_sha256'] and sha(folder/'offline-trust.bundle')==build['trust_bundle_sha256'],'Exact signed own process, Data, trust and source manifest')
require(struct.unpack_from('<4I',(folder/'air-native').read_bytes())==(0xfeedfacf,0x100000c,0,2),'Actual ordinary ARM64 process')
subprocess.run(['codesign','--verify','--strict',folder/'air-native'],check=True,capture_output=True,timeout=30)
detail=subprocess.run(['codesign','--display','--verbose=4',folder/'air-native'],check=True,capture_output=True,text=True,timeout=30).stderr
require(re.search(r'^Page size=4096$',detail,re.M),'Actual own 4K CodeDirectory')
require(modules((folder/'offline-trust.bundle').read_bytes())[1:]==modules((ROOT/'build/original-static-system-trust/original-static-system.bundle').read_bytes()),'Original trust modules unchanged')
require(not d['bounded_timeout_interrupted'] and d['qemu_accelerator']=='hvf' and d['native_4k_mmu_observed'] and not d['sheng_hardware_tested'] and d['original_amfi_table_owner_observed'] and d['original_crypto_initialized_observed'] and d['owner_root_binding_audit']['boot_root_accepted'] and d['actual_signature_failures']==dict(_cs_validate_page_bad_hash=0,_cs_validate_page_no_hash=0) and d['actual_process']['pid']==1 and d['actual_process']['name']=='air-native' and d['scratch_data']['actual_seed_sha256']==data['sha256'] and d['trust_cache_bundle_sha256']==build['trust_bundle_sha256'],'Actual original runtime, preserved AMFI/root/signatures, new signed own program and native CPU 4K')
u=d['entry_user_state_candidates'][0];v=struct.unpack('<32Q',bytes.fromhex(u['register_memory']['13:100']['bytes']))
require(not int(u['cpsr'],16)&31 and u['instruction_bytes'].startswith('000020d4') and v[:4]==(0x47505550,1,4096,4096) and v[4]>1 and v[12]>1 and v[4]!=v[12] and v[5:7]==v[13:15]==(4096,4096) and v[7] and v[15] and v[7]!=v[15] and v[8] and v[16] and v[8]!=v[16] and v[9:12]==(4096,0,4) and v[17:23]==(4096,1,4,0,0,1),'Both actual workers qualify their new original-shader path, real original IOSurfaces, foreign refusal, finish and actual waitpid exit zero')
b=d['native_gpu_broker'];require(b['stage']==3 and not b['status'] and b['clients']==b['closed']==2 and not b['active'] and not b['failures'] and b['refusals']==1 and b['requests']==137 and b['reply_bytes']==144974,'Exact real broker operations and one original foreign-resource refusal')
c=b['actual_cpu_contexts'];require(len(c)==2 and {r['pid'] for r in c}=={v[4],v[12]} and len({r['TTBR0_EL1'] for r in c})==len({r['task'] for r in c})==2,'Two distinct actual worker tasks and TTBR0 contexts')
for r in c:require(r['native_cpu_4k_accepted'] and (int(r['TCR_EL1'],16)>>14)&3==0 and (int(r['TCR_EL1'],16)>>30)&3==2 and int(r['SCTLR_EL1'],16)&1 and int(r['TTBR0_EL1'],16) and int(r['TTBR1_EL1'],16),'Actual active native CPU TG0/TG1 4K, MMU and TTBR state')
require(not any(d['native_gpu_shared_events'].values()) and d['native_original_provider']['stage']==0 and not d['native_original_provider']['allocated'],'No unrelated capability tests or original provider allocation/publication')
require(provenance['host_exit']==0 and provenance['api_validation_requested'] and provenance['report_sha256']==sha(folder/'host-enabled-report.json') and provenance['candidate_sha256']==plan['candidate_sha256'] and sha(ROOT/'build/host-metal/host-metal-originals')==provenance['process_sha256'],'Exact independent actual API-validation host provenance')
for name,digest in provenance['backend_sources'].items():require(sha(ROOT/name)==digest,'Exact host backend source '+name)
ops=host['operations'];require(host['transport_healthy'] and host['session_finished'] and host['opened_sessions']==host['closed_sessions']==2 and not host['cpu_pixel_renderer'] and not host['adreno_execution'] and not host['guest_system_device_discovery'] and not host['original_desktop'] and not host['failed_commands'] and not host['open_encoders'] and not host['aborted_encoders'] and not host['pending_submissions'] and len(ops)==b['requests'] and sum(32+o['result_bytes'] for o in ops)==b['reply_bytes'] and sum(bool(o['error']) for o in ops)==1,'Independent complete operation/result accounting and actual healthy cleanup')
require(all(o['request']==i+1 for i,o in enumerate(ops)),'Exact host global framing')
sessions={r['session'] for r in c}
for sid in sessions:
 sequence=[o['client_request'] for o in ops if o['session']==sid];require(sequence==list(range(1,len(sequence)+1)),'Refused frontend descriptors do not consume actual RPC sequence numbers')
rows=host['vertex_pipelines'];require(len(rows)==2 and {r['session'] for r in rows}==sessions,'One real original vertex pipeline per isolated worker')
for r in rows:require(r['vertex']=='std_vert0_lpf' and r['fragment']=='attachment_clear_frag_lpf' and r['attributes']==[dict(index=i,format=f,offset=o,buffer=0) for i,f,o in ((0,31,0),(1,29,16),(3,31,24))] and r['layouts']==[dict(index=0,stride=40,step=1,rate=1)],'Actual host Metal descriptor matches original native SDK fields')
black=bytes(4);red=bytes((0,0,255,255));left=(black*32+red*32)*64;right=(red*32+black*32)*64
left_hash=hashlib.sha256(left).hexdigest();right_hash=hashlib.sha256(right).hexdigest();reads=host['texture_readbacks']
require(len(reads)==8 and sum(r['sha256']==left_hash for r in reads)==2 and sum(r['sha256']==right_hash for r in reads)==2,'Four complete geometry-dependent GPU readbacks, every one of 16384 new vertex pixels independently checked')
textures={r['texture'] for r in reads if r['sha256'] in (left_hash,right_hash)}
require(len(textures)==2 and not any(r['texture'] in textures for r in host['texture_uploads']),'New vertex output textures never receive uploaded CPU pixels')
for texture in textures:require([r['sha256'] for r in reads if r['texture']==texture]==[left_hash,right_hash],'Each actual worker updates real vertex buffer coverage on the same GPU target')
require(len(host['completed_commands'])==7 and all(r['status']==4 and 0<r['gpu_start_ns']<r['gpu_end_ns'] for r in host['completed_commands']),'Four real original vertex/fragment GPU draws plus three real surface GPU submissions')
errors=(folder/'host-enabled-stderr.log').read_text();require('Metal API Validation Enabled' in errors and not any(s in errors for s in ('Validation Error','assertion failed','failed assertion','failed validation','Execution of the command buffer was aborted')),'Actual Metal API Validation enabled and clean')
(folder/'runtime-checkpoint.json').write_text(json.dumps(dict(candidate_sha256=plan['candidate_sha256'],native_sha256=plan['native_sha256'],process_sha256=build['process_sha256'],host_process_sha256=provenance['process_sha256'],report_sha256=sha(fixture/'gdb-stop.json'),actual_native_workers=2,original_vertex='std_vert0_lpf',original_fragment='attachment_clear_frag_lpf',vertex_gpu_draws=4,vertex_pixels_checked=16384,total_gpu_submissions=7,total_readbacks=8,requests=b['requests'],reply_bytes=b['reply_bytes'],api_validation=True,normal_device_discovery=False,original_desktop=False,adreno_execution=False,active_native_adreno_4k=False),indent=2)+'\n')
print('PASS: two real native4K workers, actual original QuartzCore vertex layouts/MVP/buffers, four GPU draws/all16384 pixels, real surface isolation and clean Metal validation')
print('Private offline GPU path only; original desktop, Adreno execution and active native4K GPU SMMU remain unqualified')
