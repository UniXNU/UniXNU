#!/usr/bin/env python3
"""Verify actual GPU pixels on QEMU scanout through the original pending queue."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/native-legacy-display'
sys.path.insert(0,str(ROOT/'kits/XnuPrelink'))
from native_prelink import macho,backed_offset
def require(v,s):
    if not v:raise SystemExit(s)
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
build=load(OUT/'build-report.json')
for name,digest in build['source_sha256'].items():require(sha(ROOT/name)==digest,'Exact compiled source '+name)
require(sha(OUT/'libNativeLegacyDisplay.late.a')==build['archive_sha256'] and
        build['owned_entries']==[0,1,7,14,84,86,87,141,155,184,188,211,213,245,246,288,290,296,306,307,337,338,345],
        'Actual archive and qualified original queue-kick override')
kernel=ROOT/'build/xnu-prelink/native-owner-legacy-display-transfer-ready-candidate.macho';plan=load(kernel.with_suffix('.json'))
raw=kernel.read_bytes();image=macho(raw)
require(sha(kernel)==plan['candidate_sha256'] and sha(ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')==plan['native_sha256'],'Exact current native candidate')
for module,digest in plan['original_executable_sha256'].items():
    e=next(e for e in plan['extents'] if e['module']==module and e['segment']=='__TEXT_EXEC')
    o=backed_offset(image['segments'],e['va'],e['size'],len(raw))
    require(hashlib.sha256(raw[o:o+e['size']]).hexdigest()==digest,'Whole original executable unchanged '+module)
paths=[ROOT/('build/'+name+'/gdb-stop.json') for name in (
    'darwinboot-owner-hvf-offline-legacy-swap-transfer-ready-driver-pm',
    'darwinboot-owner-hvf-offline-legacy-swap-transfer-disabled-transfer-ready-driver-pm')]
observations=[load(p) for p in paths]
for d in observations:
    l=d['native_legacy_display']
    require(d['kernel_sha256']==plan['candidate_sha256'] and not d['bounded_timeout_interrupted'] and
            d['native_4k_mmu_observed'] and d['original_amfi_table_owner_observed'] and
            d['owner_root_binding_audit']['boot_root_accepted'] and
            d['actual_signature_failures']==dict(_cs_validate_page_bad_hash=0,_cs_validate_page_no_hash=0) and
            l['stage']==10 and not l['guard_slot'] and l['object_size']==6328 and
            l['swap_validation_calls']==1 and l['swap_validation_result']==1 and l['swap_validation_reason']==0,
            'Actual original provider/validation, native 4K and original AMFI/root')
    require(d['stop_symbol']=='_exception_triage' and d['actual_process']['name']=='air-native' and d['actual_process']['pid']==1,'Actual own process boundary')
    u=d['entry_user_state_candidates'][0];v=struct.unpack('<16Q',bytes.fromhex(u['register_memory']['13:80']['bytes']))
    require(int(u['cpsr'],16)&31==0 and u['instruction_bytes'].startswith('000020d4') and
            v[:6]==(0x47505357,1,4096,4096,800,600) and v[7:12]==(480000,0,1,0,0) and
            v[13]>=24000000 and v[14:]==(1,4),'Actual completed GPU pixels, original API statuses and scheduling interval')
d,disabled=observations;l=d['native_legacy_display'];c=disabled['native_legacy_display']
require(l['transfer_calls']==1 and l['transfer_status']==0 and l['transfer_bytes']==1920000 and
        l['transfer_request']==l['swap_request'] and l['transfer_request'] and
        c['transfer_calls']==c['transfer_bytes']==0 and c['transfer_status']==-1,'Actual identical queued request copied once; disabled control does not transfer')
gpu=ROOT/'build/offline-legacy-swap';program=load(gpu/'build-report.json');data=load(gpu/'data-report.json');manifest=load(gpu/'test-inputs.json')
require(sha(gpu/'air-native')==program['process_sha256']==data['process_sha256'] and
        sha(gpu/'test-inputs.json')==program['manifest_sha256']==data['manifest_sha256'] and
        sha(gpu/'compiler-data-32.cdr')==data['sha256'],'Exact own signed/staged GPU process')
for name,digest in manifest['sources'].items():require(sha(ROOT/name)==digest,'Exact GPU source '+name)
for observation in observations:
    require(observation['scratch_data']['actual_seed_sha256']==data['sha256'] and
            observation['trust_cache_bundle_sha256']==program['trust_bundle_sha256']==sha(gpu/'offline-trust.bundle'),'Actual own Data/trust identity')
def modules(b):
    n=struct.unpack_from('<I',b)[0];offsets=struct.unpack_from('<'+'I'*n,b,4)
    return [b[a:z] for a,z in zip(offsets,(*offsets[1:],len(b)))]
require(modules((gpu/'offline-trust.bundle').read_bytes())[1:]==modules(
        (ROOT/'build/original-static-system-trust/original-static-system.bundle').read_bytes()),'Both original trust modules preserved')
for prefix in ['host-transfer-ready-driver-pm','host-transfer-disabled-transfer-ready-driver-pm']:
    host=load(gpu/f'{prefix}-report.json');commands=host['completed_commands'];readbacks=host['texture_readbacks']
    require(host['host_device']=='Apple M1' and not host['cpu_pixel_renderer'] and not host['adreno_execution'] and
            not host['original_desktop'] and len(host['operations'])==609 and
            all(not o['error'] and o['request']==i+1 for i,o in enumerate(host['operations'])) and
            host['operations'][-1]['operation']==0x10f and len(commands)==len(readbacks)==1 and
            commands[0]['status']==4 and 0<commands[0]['gpu_start_ns']<commands[0]['gpu_end_ns'] and
            readbacks[0]['bytes']==1920000 and readbacks[0]['sha256']==hashlib.sha256(struct.pack('<I',0xff336699)*480000).hexdigest(),
            'Complete actual host GPU frame in each independent run')
scanout=d['gop_scanout_observation'];require(scanout['provider']=='original-legacy-gop' and scanout['bytes']==1920000,'Actual original-backend GOP observer')
for capture in scanout['captures']:
    require(bytes.fromhex(capture['bytes'])==struct.pack('<I',0xff336699)*1024,'Actual kernel scanout samples contain completed GPU pixels')
pages=[p for span in scanout['translations'] for p in span['pages']]
require(len(pages)==469 and len({p['virtual_address'] for p in pages})==469,'All actual scanout pages walked once')
for i,p in enumerate(pages):
    require(p['leaf_level']==3 and p['leaf_bytes']==4096 and p['ap']==0 and p['pxn'] and p['uxn'] and p['accessed'] and
            int(p['virtual_address'],16)==l['gop_virtual']+4096*i and int(p['physical_address'],16)==l['gop_physical']+4096*i,
            'Each real active CPU leaf is native 4K, kernel-only and non-executable')
capture=d['qemu_screen_capture'];png=paths[0].parent/capture['file'];b=png.read_bytes()
require(sha(png)==capture['sha256']=='5c4cf16e35ac63fa0d0a6c78b7069a31b13e4685feeb07d4721b7f304ceaf708' and
        struct.unpack_from('>IIBBBBB',b,16)==(800,600,8,2,0,0,0),'Exact inspected actual QMP RGB PNG')
# Read the actual PNG; do not generate, modify or reconstruct a screenshot.
at=8;compressed=b''
while at<len(b):
    n=struct.unpack_from('>I',b,at)[0];kind=b[at+4:at+8];body=b[at+8:at+8+n]
    if kind==b'IDAT':compressed+=body
    at+=12+n
pixels=zlib.decompress(compressed);require(len(pixels)==600*2401,'Actual PNG row extent')
previous=bytearray(2400);rgb=bytearray()
for row in range(600):
    filt=pixels[row*2401];current=bytearray(pixels[row*2401+1:(row+1)*2401]);require(filt<=4,'Standard PNG filter')
    for i in range(2400):
        left=current[i-3] if i>=3 else 0;above=previous[i];corner=previous[i-3] if i>=3 else 0
        if filt==4:
            p=left+above-corner;dist=[abs(p-v) for v in (left,above,corner)];predict=(left,above,corner)[dist.index(min(dist))]
        else:predict=(0,left,above,(left+above)//2)[filt]
        current[i]=(current[i]+predict)&255
    rgb+=current;previous=current
require(rgb==bytes((51,102,153))*480000,'Every one of the 480,000 actual displayed pixels matches the GPU frame')
control=disabled['qemu_screen_capture']
require(control['sha256']==sha(paths[1].parent/control['file'])=='e90f3f3195332e37f9a95d7416dc79ca2fa63d08ed3e170f71704a5678000aaf','Disabled control retains actual previous loader frame')
(OUT/'queue-transfer-checkpoint.json').write_text(json.dumps(dict(candidate_sha256=sha(kernel),reports=[sha(p) for p in paths],
    actual_gpu_pixels_visible_in_qemu=True,all_displayed_pixels_checked=480000,active_native_cpu_4k_leaves=469,
    original_queue_retirement_implemented=False,display_fence_completed=False,physical_vblank=False,
    system_metal=False,original_desktop=False,adreno_execution=False),indent=2)+'\n')
print('PASS: real GPU -> original IOSurface/pending queue -> actual QEMU scanout; all 480,000 pixels match')
print('469 actual native CPU 4K leaves; disabled control unchanged; queue retirement/system Metal/desktop remain open')
