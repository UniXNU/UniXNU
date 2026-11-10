#!/usr/bin/env python3
"""Close the finite offline prerequisites for the held UFS diagnostic boot.

Consume existing observations instead of rerunning unchanged experiments.
No USB, device commands, image creation, or userdata-image reads. Completion
is not permission to boot, hardware success, or production iPadOS readiness.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, default=ROOT/'build/ufs-root-diagnostics')
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Invalidate an earlier decision before checking changed inputs. An error
    # must never leave a stale "complete" file at the requested output path.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(offline_preparation_complete=False,
        status='checking; incomplete unless replaced by a passing decision',
        device_action_authorized=False, user_hold_active=True), indent=2)+'\n')
    evidence = args.evidence.resolve()
    ufs = ROOT/'drivers/ShengUfs'
    inputs = {}
    gates = []

    def load(name):
        path = evidence/name
        inputs[name] = digest(path)
        return json.loads(path.read_text())

    def log_pass(name, marker='PASS:'):
        path = evidence/name
        inputs[name] = digest(path)
        require(marker in path.read_text(), 'Missing successful evidence: '+name)

    def source_hashes(report, root, key='source_sha256'):
        for name, expected in report[key].items():
            require(digest(root/name) == expected, 'Evidence source changed: '+name)

    release = load('publication/release.json')
    require(args.image.name == release['image'] and args.image.stat().st_size == release['size'], 'Wrong held image')
    require(digest(args.image) == release['image_sha256'], 'Held image changed')
    require(digest(args.candidate) == release['candidate_sha256'], 'Held candidate changed')
    # Later NativeUfs commits add tests only. Do not silently accept a driver
    # change just because an old report has a PASS string.
    revision = release['native_ufs_commit']
    original_files = subprocess.check_output(['git','-C',str(ufs),'ls-tree','--name-only',revision],text=True).splitlines()
    original_files = {n for n in original_files if n.endswith(('.cpp','.h'))}
    current_files = {p.name for p in ufs.iterdir() if p.suffix in ('.cpp','.h')}
    require(original_files == current_files, 'Production source set changed')
    for name in original_files:
        original = subprocess.check_output(['git','-C',str(ufs),'show',revision+':'+name])
        require((ufs/name).read_bytes() == original, 'Production source differs from held release: '+name)
    gates.append('frozen image, candidate and production source identity')

    for name in ('TransferPoll','RootCommands','SmmuTakeover'):
        log_pass('integration/'+name+'-test.log')
    old_command = load('integration/release/report.json')
    for name in ('RootCommands.h','RootQueue.h','RootTransportLayout.h','TransferPoll.h','tests/RootCommandsBridge.cpp'):
        require(digest(ufs/name) == old_command['source_sha256'][name], 'Command fault-test implementation changed')
    # The SMMU planner/test and publication coordinator/test are byte-identical
    # to their recorded tested revisions; diagnostic formatting is checked later.
    for revision, names in [('d3a0ba8', ('SmmuTakeover.h','tests/SmmuTakeover.cpp','tests/TransferPoll.cpp','tests/RootCommands.cpp')),
                            (release['native_ufs_commit'], ('RootPublication.h','tests/RootPublication.cpp'))]:
        for name in names:
            require((ufs/name).read_bytes() == subprocess.check_output(['git','-C',str(ufs),'show',revision+':'+name]),
                    'Host fault-test source changed: '+name)
    gates.append('queue, completion, protocol and SMMU refusal tests')

    protocol = load('publication/qemu/report.json')
    source_hashes(protocol, ufs)
    source_hashes(protocol, ROOT/'kits/VerifiedRoot', 'verified_root_sha256')
    require({r['dma'] for r in protocol['results']} == {'0x40010000','0x8cb5e9000'}, 'Missing modeled DMA addresses')
    for result in protocol['results']:
        require(all(result[k] == 'pass' for k in ('nop','read_4k','read_128k','bad_lba_no_copy')), 'UFS model failed')
        require(all(v == 'pass' for v in result['root_path'].values()), 'Signed root path model failed')
    for name in ('RootLayout','RootWindowRead','RootPublication'):
        log_pass('publication/host/'+name+'.log')
    gates.append('GPT, manifest, owner verification, window reads and publication failure handling')

    arm = load('allocation/arm64-sharing/report.json')
    source_hashes(arm, ufs)
    require({r['case'] for r in arm['results']} == {'low','high','high-inner-shareable','truncated-high','virtual-as-physical'},
            'Missing ARM64 case')
    require(all(r['passed'] for r in arm['results']), 'ARM64 command case failed')
    legacy = load('arm64-command/legacy/report.json')
    source_hashes(legacy, ufs)
    require(legacy['passed'] and legacy['cases'] == 14, 'Historical descriptor comparison failed')
    disassembly = load('arm64-command/held-kernel-audit.json')
    require(disassembly['candidate_sha256'] == release['candidate_sha256'], 'Wrong disassembled candidate')
    require(digest(evidence/'arm64-command/held-kernel-command.disasm') == disassembly['disassembly_sha256'], 'Disassembly changed')
    gates.append('ARM64 cache/MMIO execution, DMA width and held-kernel instruction audit')

    xnu = load('allocation/tcg/gdb-stop.json')
    require(xnu['kernel_sha256'] == release['candidate_sha256'] and not xnu['bounded_timeout_interrupted'], 'Wrong/incomplete XNU run')
    allocation = xnu['ufs_allocation_exercise']
    require(all(allocation[k] for k in ('passed','registers_restored','debugger_invoked')), 'Allocation exercise incomplete')
    require(allocation['source_sha256'] == digest(ROOT/'scripts/qemu-entry/ufs_allocation.py'), 'Allocation observer changed')
    require(len(allocation['pages']) == 34 and len(allocation['calls']) == 39 and allocation['contiguous'] == 139264,
            'Incomplete actual allocation observation')
    require(allocation['ufs_counters_before'] == allocation['ufs_counters_after'] and
            not any(allocation['ufs_counters_after'].values()), 'Unexpected UFS activity')
    base = int(allocation['physical'],16)
    for index, page in enumerate(allocation['pages']):
        require(int(page['pa'],16) == base+index*4096 and page['level'] == 3 and page['ap'] == 0 and
                page['accessed'] and page['mair_byte'] == 255 and page['shareability'] == 2, 'Unexpected active DMA PTE')
    gates.append('actual XNU allocation, every active 4K DMA PTE and bounds')

    pmgr = load('allocation/tcg/pmgr-checked.json')
    require(pmgr['kernel_sha256'] == release['candidate_sha256'] and pmgr['amfi_lookup_qualified'] and
            pmgr['mode'] == 'amfi' and pmgr['accelerator'] == 'tcg', 'AMFI checkpoint not qualified')
    prelink = json.loads(args.candidate.with_suffix('.json').read_text())
    original = json.loads((args.candidate.parent/'native-owner-stage5-candidate.json').read_text())
    require(prelink['candidate_sha256'] == release['candidate_sha256'] and not prelink['source_inputs_modified'], 'Prelink identity mismatch')
    require(len(prelink['original_executable_sha256']) == 29 and
            prelink['original_executable_sha256'] == original['original_executable_sha256'], 'Original executable components changed')
    log_pass('publication/crossbuild.log', '-Werror build and actual ARM64/iOS 17 object audit passed')
    gates.append('strict driver build, original component hashes and original AMFI checkpoint')

    package = load('publication/final-package-audit/report.json')
    for field in ('image_sha256','candidate_sha256','embedded_kernel_sha256'):
        require(package[field] == release[field], 'Final-container identity mismatch: '+field)
    require(package['patch_reproduction'] == 'byte-for-byte match' and package['owned_memory'] == '0x40000000', 'Wrong packaged kernel/window')
    require(package['boot_args'] == ['-v','serial=3','debug=0x14e','kt_fixed_zones=120','pmgr=2','native-ufs-root=1','native-ufs-diagnostics=1'],
            'Unexpected probe/reset/security arguments')
    log_pass('publication/audit-controls.log', 'PASS: 15 negative packaging controls')
    gates.append('actual Android/FAT/kernel/firmware/ADT/root UUID/Data consistency and refusal controls')

    renderer = load('publication/renderer/report.json')
    require(len(renderer['matched_lines']) == 28 and not renderer['hardware_or_xnu_boot_qualified'], 'Incomplete/mislabeled screen observation')
    for prefix in ('QUEUE ','FAULT ','UIC ','IO ','Waiting for signed UUID ','TCR_EL1','max_mem'):
        require(any(line.startswith(prefix) for line in renderer['matched_lines']), 'Missing screen evidence: '+prefix)
    log_pass('publication/renderer.log', 'draws all 28 expected lines')
    gates.append('single-screen diagnostic capacity and actual ARM64 renderer')

    report = dict(scope='Offline prerequisites for the frozen UFS diagnostic boot only',
                  offline_preparation_complete=True, required_offline_items_remaining=[],
                  device_action_authorized=False, user_hold_active=True, hardware_success=False,
                  production_ipados_ready=False, boot_sent=False, gates=gates,
                  image=release['image'], image_sha256=release['image_sha256'],
                  candidate_sha256=release['candidate_sha256'], evidence_sha256=inputs,
                  production_revision=release['native_ufs_commit'],
                  source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  checker_sha256=digest(Path(__file__)),
                  reopen_only_for=['changed candidate/source/configuration', 'new hardware observation',
                                   'new concrete contradictory evidence', 'changed user objective'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(gates)} prerequisite groups; required offline items remaining: 0; device hold remains active')


if __name__ == '__main__':
    main()
