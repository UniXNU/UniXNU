#!/usr/bin/env python3
"""Check actual IOKit logical scanout callbacks, controls and next refusal."""
import hashlib
import json
from pathlib import Path
import struct
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'kits/XnuPrelink'))
from native_prelink import macho,backed_offset
def require(v,s):
    if not v:raise SystemExit(s)
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
build=load(ROOT/'build/native-legacy-display/build-report.json')
for name,digest in build['source_sha256'].items():require(sha(ROOT/name)==digest,'Exact compiled source '+name)
require(sha(ROOT/'build/native-legacy-display/libNativeLegacyDisplay.late.a')==build['archive_sha256'] and
        build['owned_entries']==[0,1,7,14,84,86,87,141,155,184,188,211,213,245,246,288,306,307,337,338,345],
        'Exact compiled archive and qualified lifecycle overrides')
kernel=ROOT/'build/xnu-prelink/native-owner-legacy-display-pm-candidate.macho';plan=load(kernel.with_suffix('.json'))
raw=kernel.read_bytes();image=macho(raw)
require(sha(kernel)==plan['candidate_sha256'] and sha(ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')==plan['native_sha256'], 'Exact current native candidate')
for module,digest in plan['original_executable_sha256'].items():
    e=next(e for e in plan['extents'] if e['module']==module and e['segment']=='__TEXT_EXEC')
    o=backed_offset(image['segments'],e['va'],e['size'],len(raw))
    require(hashlib.sha256(raw[o:o+e['size']]).hexdigest()==digest,'Unchanged whole original executable '+module)
paths=[ROOT/('build/darwinboot-owner-hvf-offline-legacy-swap-pm'+suffix+'/gdb-stop.json') for suffix in ('','-submit','-validate')]
observations=[load(p) for p in paths]
for d in observations:
    l=d['native_legacy_display']
    require(d['kernel_sha256']==plan['candidate_sha256'] and not d['bounded_timeout_interrupted'] and
            d['native_4k_mmu_observed'] and d['original_amfi_table_owner_observed'] and
            d['owner_root_binding_audit']['boot_root_accepted'] and
            d['actual_signature_failures']==dict(_cs_validate_page_bad_hash=0,_cs_validate_page_no_hash=0), 'Native 4K and original AMFI/root')
    require(l['pm_stage']==4 and l['pm_status']==0 and l['pm_callbacks']==1 and l['pm_calls']==4 and
            l['pm_ordinal']==1 and l['stage']==10 and l['guard_slot']==0,'Actual IOKit registration/request/callback and original return')
d,submit,validation=observations
values=struct.unpack('<16Q',bytes.fromhex(d['entry_user_state_candidates'][0]['register_memory']['13:80']['bytes']))
require(d['stop_symbol']=='_exception_triage' and values[:6]==(0x47505357,1,4096,4096,800,600) and
        values[7:12]==(480000,0,1,0,0xe00002c2) and values[13]>=24000000 and values[14:]==(1,4), 'Real GPU pixels and deeper original BadArgument after one actual second')
tail=bytes.fromhex(submit['entry_regions']['0:1000:800']['bytes'])
require(int(submit['pc'],16)==0xfffffff00578f224 and struct.unpack_from('<2I',tail,5836-4096)==(1,0), 'Actual original controller scheduling state is 1; no panel power completion')
require(validation['function_return_stack_matched'] and int(validation['x0'],16)==0 and
        int(validation['finished_function_entry'],16)==0xfffffff005795bb4 and int(validation['pc'],16)==0xfffffff005790ed0,
        'Original mandatory backend validator really returns false to its unchanged caller')
surface=bytes.fromhex(validation['entry_indirect_memory']['1:a40:100']['bytes'])
require(struct.unpack_from('<3Q',surface,88)==(800,600,3200) and struct.unpack_from('<I',surface,128)[0]==0x42475241 and
        struct.unpack_from('<Q',surface,144)[0]==1920000 and struct.unpack_from('<I',surface,152)[0]==0 and
        struct.unpack_from('<Q',surface,48)[0], 'Actual original nonplanar BGRA IOSurface and backing descriptor')
init=load(ROOT/'build/darwinboot-owner-hvf-legacy-display-init-pm-control/gdb-stop.json')
off=load(ROOT/'build/darwinboot-owner-hvf-legacy-display-default-off-pm-control/gdb-stop.json')
require(init['native_legacy_display']['stage']==8 and init['native_legacy_display']['released']==1 and
        init['native_legacy_display']['pm_calls']==0 and not off['bounded_timeout_interrupted'] and
        off['stop_symbol']=='original-launchd-main' and off['native_legacy_display']['pm_calls']==0 and
        off['native_legacy_display']['stage']==0 and off['native_4k_mmu_observed'], 'Real release and default-off original-main controls')
(ROOT/'build/native-legacy-display/logical-pm-checkpoint.json').write_text(json.dumps(dict(
    candidate_sha256=sha(kernel),reports=[sha(p) for p in paths],actual_logical_callback=True,
    actual_controller_state=1,actual_panel_state=0,actual_backend_validation=False,
    physical_power_control=False,original_desktop=False,adreno_execution=False),indent=2)+'\n')
print('PASS: actual IOKit logical scheduling callback and controller state 1, with real init/default-off controls')
print('Original mandatory backend validator returns false; no completed frame, panel power, system Metal or desktop claim')
