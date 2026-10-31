#!/usr/bin/env python3
"""Qualify original Legacy lifecycle and preserve its real backend refusal."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/native-legacy-display'
sys.path.insert(0, str(ROOT / 'kits/XnuPrelink'))
from native_prelink import macho, backed_offset


def require(value, reason):
    if not value:
        raise SystemExit(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


build = json.loads((OUT / 'build-report.json').read_text())
for name, digest in build['source_sha256'].items():
    require(sha(ROOT / name) == digest, 'Exact current source: ' + name)
for name, key in [('OriginalLegacyFramebufferABI.h', 'generated_abi_sha256'),
                  ('NativeLegacyDisplay.o', 'compiled_object_sha256'),
                  ('NativeLegacyDisplay.late.o', 'late_object_sha256'),
                  ('libNativeLegacyDisplay.late.a', 'archive_sha256')]:
    require(sha(OUT / name) == build[key], 'Exact actual build: ' + name)
require(build['virtual_entries'] == 358 and build['owned_entries'] ==
        [0, 1, 7, 84, 211, 213, 245, 246, 288, 306, 307, 337, 338, 345],
        'Only qualified own methods and guarded abstract leaves')

candidate = ROOT / 'build/xnu-prelink/native-owner-legacy-display-gop-candidate.macho'
plan = json.loads(candidate.with_suffix('.json').read_text())
raw = candidate.read_bytes()
image = macho(raw)
require(sha(candidate) == plan['candidate_sha256'], 'Exact observed candidate')
native = ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped'
require(sha(native) == plan['native_sha256'], 'Current native source kernel')
for family, digest in plan['original_executable_sha256'].items():
    extents = [e for e in plan['extents'] if e['module'] == family and e['segment'] == '__TEXT_EXEC']
    require(len(extents) == 1, 'Unambiguous original executable extent')
    e = extents[0]
    at = backed_offset(image['segments'], e['va'], e['size'], len(raw))
    require(hashlib.sha256(raw[at:at + e['size']]).hexdigest() == digest,
            'Complete original instructions unchanged: ' + family)

observations = {}
for case in ['init', 'start', 'headless', 'default-off', 'start-error']:
    path = ROOT / ('build/darwinboot-owner-hvf-legacy-display-' + case + '-gop-control/gdb-stop.json')
    d = json.loads(path.read_text())
    require(d['kernel_sha256'] == plan['candidate_sha256'] and
            d['qemu_accelerator'] == 'hvf' and not d['bounded_timeout_interrupted'],
            'Same actual bounded candidate: ' + case)
    regs = {k: int(v, 16) for k, v in d['system_registers'].items()}
    require(d['native_4k_mmu_observed'] and (regs['TCR_EL1'] >> 14) & 3 == 0 and
            (regs['TCR_EL1'] >> 30) & 3 == 2 and regs['SCTLR_EL1'] & 1 and
            regs['TTBR0_EL1'] and regs['TTBR1_EL1'], 'Actual native CPU 4K: ' + case)
    state = d['native_legacy_display']
    require(not state['gop_map'] and not state['gop_width'], 'Backend gate remains disabled: ' + case)
    require(not state['guard_slot'], 'No unclassified backend leaf executed: ' + case)
    video = d['actual_boot_video']['pe_video']
    if case == 'headless':
        require(state['stage'] == 2 and state['meta_status'] == 0 and
                not state['object'] and not any(video.values()), 'No-video creation refusal')
    elif case == 'default-off':
        require(state['stage'] == 0 and state['meta_status'] == -1 and
                d['original_launchd_main_executed'] and d['followed_main_entry']['first_instruction_completed'] and
                d['original_amfi_table_owner_observed'] and d['owner_root_binding_audit']['boot_root_accepted'] and
                d['owner_root_binding_audit']['_native_owner_root_apple_autherr'] == 80 and
                set(d['direct_user_commpage_shifts'].values()) == {12} and
                d['actual_signature_failures'] == dict(_cs_validate_page_bad_hash=0, _cs_validate_page_no_hash=0),
                'Default-off original launchd/AMFI/root/native user 4K')
    else:
        require(state['meta_status'] == 0 and state['init_result'] == 1 and
                state['object_size'] == 0x18a0 and state['parent_match'] == 1 and state['object'],
                'Real original init/object/parent: ' + case)
        if case == 'start-error':
            require(int(d['pc'], 16) == 0xfffffff0057870b0 and int(d['x30'], 16) == 0xfffffff005787f1c and
                    d['argument_memory']['x1'] == 'start_hardware failed\n' and state['stage'] == 5,
                    'Real original failure and exact original callsite')
        else:
            require(d['stop_symbol'] == '_native_legacy_display_checkpoint' and
                    state['stage'] == 8 and state['released'] == 1, 'Actual completed release: ' + case)
        if case.startswith('start'):
            require(state['probe_match'] == 1 and not state['start_result'] and
                    state['surface_status'] == 0 and state['surface_found'] == 1 and
                    state['video_base'] == video['v_baseAddr'] and
                    state['video_bytes'] == video['v_rowBytes'] * video['v_height'] == 1920000,
                    'Actual GOP resources and real IOSurface dependency; original start refuses')
    observations[case] = dict(checkpoint_sha256=sha(path), state=state, actual_tcr=regs['TCR_EL1'])

for case in ['mapped', 'publication']:
    path = ROOT / ('build/darwinboot-owner-hvf-legacy-display-start-gop-' + case + '/gdb-stop.json')
    d = json.loads(path.read_text())
    require(d['kernel_sha256'] == plan['candidate_sha256'] and not d['bounded_timeout_interrupted'] and
            d['qemu_accelerator'] == 'hvf' and d['native_4k_mmu_observed'], 'Actual gated GOP observation')
    state = d['native_legacy_display']
    video = d['actual_boot_video']['pe_video']
    require(state['stage'] == 5 and state['init_result'] == state['probe_match'] == state['parent_match'] == 1 and
            state['surface_status'] == 0 and state['surface_found'] == 1 and not state['guard_slot'] and
            not state['released'] and state['object_size'] == 6304, 'Original start reaches actual backend')
    require(state['gop_map'] and state['gop_virtual'] and
            state['gop_physical'] == state['video_base'] == video['v_baseAddr'] and
            state['gop_bytes'] == state['video_bytes'] == video['v_rowBytes'] * video['v_height'] == 1920000 and
            state['gop_width'] == video['v_width'] == 800 and state['gop_height'] == video['v_height'] == 600,
            'Real retained framebuffer mapping and original geometry getter use actual GOP mode')
    if case == 'mapped':
        require(d['stop_symbol'] == '_native_legacy_gop_mapping_checkpoint', 'Actual mapped checkpoint')
    else:
        require(int(d['pc'], 16) == 0xfffffff0057880d4, 'Original service-publication call not yet executed')
    observations['gop-' + case] = dict(checkpoint_sha256=sha(path), state=state)

(OUT / 'native-checkpoint.json').write_text(json.dumps(dict(
    candidate_sha256=plan['candidate_sha256'], native_sha256=plan['native_sha256'],
    source_sha256=build['source_sha256'], observations=observations,
    actual_original_init_and_release=True, actual_original_start=False,
    original_start_failure='start_hardware failed', original_instructions_modified=False,
    actual_gop_mapping_and_mode=True, original_publication_boundary_reached=True,
    display_backend_complete=False, presentation=False, system_metal_device=False,
    original_desktop=False, hardware_tested=False), indent=2) + '\n')
print('PASS: actual GOP mapping/original mode getter and original pre-publication boundary; gated-off backend refuses')
print('Headless refuses; default-off original launchd/AMFI/root/native CPU/user 4K preserved; desktop absent')
