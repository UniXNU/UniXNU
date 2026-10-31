#!/usr/bin/env python3
"""Verify real GOP display discovery and the unchanged original client factory."""
import argparse
import hashlib
import mmap
import struct
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/native-legacy-display'
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--profile',choices=['pitch','info','scale'],default='scale');args=parser.parse_args()
sys.path.insert(0,str(ROOT/'kits/XnuPrelink'))
from native_prelink import macho,backed_offset,unserialize_xml
def require(v,reason):
    if not v:raise SystemExit(reason)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=json.loads((OUT/'build-report.json').read_text())
for name,digest in build['source_sha256'].items():require(sha(ROOT/name)==digest,'Exact current compiled source '+name)
revision=subprocess.check_output(['git','-C',ROOT/'drivers/GopFramebuffer','rev-parse','HEAD'],text=True).strip()
for name in ['NativeLegacyDisplay.cpp','NativeGOPPresenter.cpp','NativeGOPWire.h']:
    data=subprocess.check_output(['git','-C',ROOT/'drivers/GopFramebuffer','show',revision+':'+name])
    require(hashlib.sha256(data).hexdigest()==sha(ROOT/'drivers/GopFramebuffer'/name),'Exact committed driver source')
require(sha(OUT/'libNativeLegacyDisplay.late.a')==build['archive_sha256'] and
        sha(OUT/'OriginalLegacyFramebufferABI.h')==build['generated_abi_sha256'],'Exact late archive and generated ABI')
require(build['virtual_entries']==358 and build['owned_entries']==[0,1,7,14,84,87,141,184,188,211,213,245,246,288,306,307,337,338,345],
        'Exact qualified own overrides and remaining guarded leaves')
audit=json.loads((ROOT/'build/display-analysis/mobile-graphics-legacy-abi.json').read_text())
require(int(build['bindings']['__ZTV25IOMobileFramebufferLegacy'],16)==int(audit['legacy_vptr'],16)-16,
        'Apple-kext qualified super calls bind the real original vtable header')
candidate=ROOT/('build/xnu-prelink/native-owner-legacy-display-'+args.profile+'-candidate.macho');plan=json.loads(candidate.with_suffix('.json').read_text())
raw=candidate.read_bytes();image=macho(raw)
require(sha(candidate)==plan['candidate_sha256'] and sha(ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')==plan['native_sha256'],
        'Exact current source kernel and original-family candidate')
for module,digest in plan['original_executable_sha256'].items():
    extent=next(e for e in plan['extents'] if e['module']==module and e['segment']=='__TEXT_EXEC')
    at=backed_offset(image['segments'],extent['va'],extent['size'],len(raw))
    require(hashlib.sha256(raw[at:at+extent['size']]).hexdigest()==digest,'Whole original executable unchanged: '+module)

# Qualify the actual uint32 output / IOReturn slot-188 contract and its
# missing-property result, rather than giving an opaque method a guessed ABI.
for address,size,digest in [
    (0xfffffff005798184,312,'6c161fa48818f254191d915cc99318e085a1555d7ddbd003b86ccd75034ba363'),
    (0xfffffff005778168,56,'b925b4b5bb870637ace1f46bc14010bf5d473edbeb6eaecd9d898fedbc8ee465'),
    (0xfffffff00577a554,88,'6d8ebdd3591475c418f3632d112cad88a12cc4a53fa6733190531aa0e56d46c8')]:
    at=backed_offset(image['segments'],address,size,len(raw))
    require(hashlib.sha256(raw[at:at+size]).hexdigest()==digest,'Exact original dot-pitch implementation/callers')
pitch_path=ROOT/('build/darwinboot-owner-hvf-legacy-display-start-'+args.profile+'-dotpitch/gdb-stop.json')
pitch=json.loads(pitch_path.read_text())
require(pitch['kernel_sha256']==plan['candidate_sha256'] and not pitch['bounded_timeout_interrupted'] and
        int(pitch['pc'],16)==0xfffffff005778194 and int(pitch['x0'],16)==0xe00002f0,
        'Actual original caller receives genuine missing dot-pitch error')
frame=pitch['frame_chain'][1];data=bytes.fromhex(frame['local_bytes'])
offset=int(pitch['frame_chain'][0]['fp'],16)+16-int(frame['local_address'],16)
require(data[offset:offset+4]==bytes(4),'Actual uint32 output is initialized to zero on missing metadata')
require(pitch['native_legacy_display']['client_calls']>=2 and not pitch['native_legacy_display']['guard_slot'],
        'Real system clients reach the query without a backend guard')

frame_info_observation=None
if args.profile in ('info','scale'):
    require(build['guarded_backend_leaves']==[211,245,246,306,307,337,338,345],
            'Eight unclassified leaves remain guarded; optional frame tracing is explicitly unsupported')
    for address,size,digest in [
        (0xfffffff005778688,152,'1dda59338b977c6c2ea0556d397e5ae26ace30d6c8c86fdceea18036ffb5b4c7'),
        (0xfffffff00577a718,88,'9ffaf7219e50c6134bdc72fe51eff26de43ed27de4fe37fd0a05fff68771dc84'),
        (0xfffffff005f35bb0,24,'75e1cd2260e703a28d2a5e7cf2ed1bbe0b1d4b49359860c12d55634dc85a805b')]:
        at=backed_offset(image['segments'],address,size,len(raw))
        require(hashlib.sha256(raw[at:at+size]).hexdigest()==digest,'Exact original frame-info ABI and selector 74 dispatch')
    # Original userspace enumerates fixed 64-byte key names with strndup;
    # failure / zero count follows its real optional-capability path.
    cache=ROOT/'.cache/firmware/target-volumes/systemos-mount/System/Library/Caches/com.apple.dyld'
    wanted={0x1b63d53f8:(432,'6a6d646a0ffbbd9ff528d7ec73b7b451af4f33c765ceb02c06c6bffdad77d881'),
            0x1b63d65b0:(172,'e506fe8d7ec92144364bcdbcc5bf519569da6f30b319e24ccfc9a44803a228af')}
    found=set()
    for path in sorted(cache.glob('dyld_shared_cache_arm64*')):
        if path.suffix=='.symbols':continue
        with path.open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as mapping:
            require(mapping[:16].rstrip(bytes(1))==b'dyld_v1   arm64','Original ARM64 shared-cache format')
            table,count=struct.unpack_from('<2I',mapping,16)
            for index in range(count):
                va,size,offset,_,protection=struct.unpack_from('<3Q2I',mapping,table+index*32)
                for address,(length,digest) in wanted.items():
                    if va<=address and address+length<=va+size:
                        at=offset+address-va
                        require(protection&4 and hashlib.sha256(mapping[at:at+length]).hexdigest()==digest,
                                'Exact unchanged original userspace trace-key enumeration')
                        found.add(address)
    require(found==set(wanted),'Both original userspace frame-info functions are present')
    path=ROOT/('build/darwinboot-owner-hvf-legacy-display-start-'+args.profile+'-frameinfo-return/gdb-stop.json')
    d=json.loads(path.read_text())
    require(d['kernel_sha256']==plan['candidate_sha256'] and not d['bounded_timeout_interrupted'] and
            int(d['pc'],16)==0xfffffff0057786e8 and int(d['x0'],16)==0xe00002c7,
            'Original frame-info caller receives genuine unsupported status')
    data=bytes.fromhex(d['stack_bytes']);require(data[16:24]==bytes(8),'Both actual frame-info scalar outputs are zero')
    require(bytes.fromhex(d['frame_indirect_memory']['0:-20:40']['bytes'])==bytes(64),'Actual fixed-size trace-key output is cleared')
    require(not d['native_legacy_display']['guard_slot'] and d['native_legacy_display']['client_calls']>=2,
            'Optional frame-info query returns after actual system-client creation')
    frame_info_observation=dict(checkpoint_sha256=sha(path),status=0xe00002c7,trace_keys_supported=False)

observations={}
for case,directory in [('client','start-'+args.profile+'-client'),('init','init-'+args.profile+'-control'),('default-off','default-off-'+args.profile+'-control')]:
    path=ROOT/('build/darwinboot-owner-hvf-legacy-display-'+directory+'/gdb-stop.json');d=json.loads(path.read_text())
    require(d['kernel_sha256']==plan['candidate_sha256'] and not d['bounded_timeout_interrupted'] and d['qemu_accelerator']=='hvf','Actual bounded same-candidate observation '+case)
    regs={k:int(v,16) for k,v in d['system_registers'].items()}
    require(d['native_4k_mmu_observed'] and (regs['TCR_EL1']>>14)&3==0 and (regs['TCR_EL1']>>30)&3==2 and
            regs['SCTLR_EL1']&1 and regs['TTBR0_EL1'] and regs['TTBR1_EL1'],'Actual native 4K CPU translation')
    state=d['native_legacy_display'];require(not state['guard_slot'],'No unclassified backend called before this boundary')
    if args.profile=='scale':
        require(state['unit_scale_calls']==(1 if case=='client' else 0) and
                state['chosen_scale']==(1 if case=='client' else 0) and not state['chosen_rotation'] and
                (state['unit_scale_status']==0 if case=='client' else state['unit_scale_status']!=0),
                'Actual unit-scale metadata is published only after the explicit mapped GOP system experiment')
    if case=='init':
        require(state['stage']==8 and state['released']==1 and state['init_result']==state['parent_match']==1 and
                state['object_size']==6320 and not state['registration_calls'] and not state['dt_attached'] and not state['client_calls'],
                'Real initialized derived object releases through original free without publication')
    elif case=='client':
        require(d['stop_symbol']=='_native_legacy_client_checkpoint' and state['stage']==10 and
                state['init_result']==state['start_result']==state['probe_match']==state['parent_match']==1 and
                state['object_size']==6320 and state['registration_calls']==state['dt_attached']==1 and not state['released'],
                'Original start completes and actual GOP subsystem is registered/attached')
        video=d['actual_boot_video']['pe_video']
        require(state['gop_map'] and state['gop_virtual'] and state['gop_physical']==video['v_baseAddr']==state['video_base'] and
                state['gop_bytes']==state['video_bytes']==video['v_rowBytes']*video['v_height']==1920000 and
                state['gop_width']==video['v_width']==800 and state['gop_height']==video['v_height']==600,
                'Actual retained GOP mapping and original mode')
        props=unserialize_xml(d['native_legacy_properties'].encode())
        require(props['IOMFB Debug Info']['Global']['width']==800 and props['IOMFB Debug Info']['Global']['height']==600 and
                'NativeGOPFramebufferMapping' not in props,'Real original property serialization with no unencodable mapping object')
        require(state['client_calls']==1 and state['client_type']==state['client_status']==0 and state['client_pid']>1 and
                state['client_task'] and state['client_object'] and d['native_legacy_client_class']=='IOMobileFramebufferUserClient',
                'Original system process creates the genuine original userclient through original newUserClient')
    else:
        require(d['original_launchd_main_executed'] and d['followed_main_entry']['first_instruction_completed'] and
                state['stage']==0 and state['meta_status']==-1 and not state['registration_calls'] and not state['dt_attached'] and not state['client_calls'],
                'Default-off original launchd without display experiment')
    if case!='init':
        require(d['original_amfi_table_owner_observed'] and d['owner_root_binding_audit']['boot_root_accepted'] and
                d['owner_root_binding_audit']['_native_owner_root_apple_autherr']==80 and
                d['actual_signature_failures']==dict(_cs_validate_page_bad_hash=0,_cs_validate_page_no_hash=0),
                'Original AMFI/Apple rejection and independent owner-root acceptance')
        shifts=d['commpage_user64_shifts'] if case=='client' else d['direct_user_commpage_shifts']
        require(set(shifts.values())=={12},'Actual native user page ABI')
    observations[case]=dict(checkpoint_sha256=sha(path),state=state,actual_tcr=regs['TCR_EL1'])
(OUT/'system-client-checkpoint.json').write_text(json.dumps(dict(candidate_sha256=plan['candidate_sha256'],native_sha256=plan['native_sha256'],
    driver_revision=revision,observations=observations,frame_info=frame_info_observation,dot_pitch_checkpoint_sha256=sha(pitch_path),missing_dot_pitch_return=0xe00002f0,actual_original_start=True,actual_system_client_created=True,
    original_instructions_modified=False,swap_contract_complete=False,system_metal_device=False,original_desktop=False,
    adreno_execution=False,hardware_tested=False),indent=2)+'\n')
print('PASS: real GOP subsystem discovery, original framebuffer start and original system-process userclient creation')
print('Init/release and default-off controls, original AMFI/root/native 4K pass; actual swaps, system Metal and desktop remain open')
