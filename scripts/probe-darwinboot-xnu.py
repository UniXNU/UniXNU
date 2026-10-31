#!/usr/bin/env python3
"""Verify native 4K XNU translation after the real UEFI/UniXNU handoff."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import uuid
from unixnu.package import output_dir

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--kernel', type=Path, default=ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped')
parser.add_argument('--output', type=Path, default=ROOT / 'build/darwinboot-xnu')
parser.add_argument('--timeout', type=int, choices=range(1, 1801), default=25, help='Bounded guest deadline: up to 300 seconds, or 1800 for explicit live HID control')
parser.add_argument('--mutate-target-main-page', action='store_true', help='Negative input control: corrupt only the actual launchd LC_MAIN vnode page before genuine validation, preserving original files/signatures')
parser.add_argument('--follow-target-main', action='store_true', help='Follow actual original dyld startup to the supplied launchd LC_MAIN and its first completed instruction')
parser.add_argument('--target-main-executable', type=Path, help='Existing unchanged target launchd for LC_MAIN observation; exact target hash is still required')
parser.add_argument('--follow-metal-device',action='store_true',help='Observe actual backboardd original MTLCreateSystemDefaultDevice return without replacing discovery')
parser.add_argument('--follow-display-mode',action='store_true',help='Observe genuine original SpringBoard display-mode initializer return, using exact cache/process activation')
parser.add_argument('--follow-display-query', action='store_true', help='After original launchd main, observe the unchanged QuartzCore query and actual server reply using its audited cache plan')
parser.add_argument('--follow-original-user-plan',type=Path,help='Read-only original user-function observation with an exact cache/native-kernel-bound plan')
parser.add_argument('--follow-display-discovery', action='store_true', help='After original launchd main, observe original IOMobileFramebuffer discovery and actual registry-derived counts')
parser.add_argument('--inspect-current-process', action='store_true', help='Read the actual current process through compiler-qualified kernel thread/process fields')
parser.add_argument('--inspect-process-list', action='store_true', help='Read the actual kernel allproc list once at the final stop')
parser.add_argument('--inspect-ui-threads', action='store_true', help='Read bounded saved thread states for original SpringBoard/backboardd at the final stop')
parser.add_argument('--capture-scratch-data', action='store_true', help='Export the actual paused mutable Data RAM disk for offline read-only inspection')
parser.add_argument('--inspect-mac-policies',action='store_true',help='Read real registered MAC policy names and exec/fork hooks using actual compiler layouts')
parser.add_argument('--follow-cache-leaf', action='store_true', help='Observe the original public getuid cache entry, real SVC and genuine return')
parser.add_argument('--log-kernel-strings-after', help='Observe bounded genuine printf format strings and stack arguments after this kernel function entry')
parser.add_argument('--log-syscall-number', type=int, action='append', default=[], help='Keep only these actual syscall events in the bounded capture')
parser.add_argument('--log-syscalls-after', help='Arm bounded genuine saved-syscall observation only after this actual kernel entry')
parser.add_argument('--log-syscalls', action='store_true', help='Capture bounded real Darwin saved syscall states')
parser.add_argument('--entry-after', help='Arm the primary observation only after this actual kernel function entry')
parser.add_argument('--native-air-init', '--native-graphics-init', dest='native_air_init', action='store_true', help='Explicit offline own signed graphics instrument in the existing init slot; never a desktop result')
parser.add_argument('--break-symbol', default='_panic')
parser.add_argument('--inspect-sheng-pmgr', action='store_true', help='Read the opt-in original PMGR lifecycle observations')
parser.add_argument('--break-address', type=lambda value: int(value, 0), help='Observe a qualified original component address with an exact prelink report')
parser.add_argument('--require-crypto14', action='store_true', help='Require the real provider and PRNG to have completed initialization')
parser.add_argument('--owned-memory-size', type=lambda value: int(value, 0), help='Request this many real UEFI-owned bytes through the DarwinBoot DT property')
parser.add_argument('--qemu-memory-mib', type=int, choices=[1024, 2048, 4096, 8192], default=1024,
                    help='Actual offline VM RAM; DarwinBoot must still allocate its entire separate requested window')
parser.add_argument('--qemu-accel', choices=['tcg', 'hvf'], default='tcg', help='Offline test accelerator; HVF requires explicit actual QEMU VMM identity')
parser.add_argument('--zone-pgz-probe-case', type=int, choices=[1, 2, 3, 4], help='Run the explicit opt-in owned allocator fixture: positive, misaligned, wrong-zone, freed')
parser.add_argument('--capture-qemu-screen',action='store_true',help='Read actual paused QEMU scanout through QMP screendump')
parser.add_argument('--qemu-ramfb', action='store_true', help='Attach actual offline ramfb and pass firmware GOP through the loader')
parser.add_argument('--qemu-ramfb-high-resolution', action='store_true', help='Explicit QEMU-only real 3048x2032 ramfb allocation/SetMode fixture')
parser.add_argument('--virtio-console-socket', type=Path, help='Existing private offline GPU transport Unix socket; QEMU only')
parser.add_argument('--inspect-boot-video', action='store_true', help='Read actual boot_args and PE video state using compiler-derived layout')
parser.add_argument('--qemu-vmm-present', action='store_true', help='Declare actual QEMU identity in the offline DT defaults; not a sheng deployment setting')
parser.add_argument('--armvirt', action='store_true', help='Use actual QEMU virt/GICv3 DT data and inspect platform discovery')
parser.add_argument('--armdt-platform', action='store_true', help='Use the sheng-shaped DT root compatible with actual QEMU GICv3 resources; exercises ArmDTPlatform, not a sheng MMIO observation')
parser.add_argument('--owner-root-audit', action='store_true', help='Observe actual root media/UUID/verified-provider binding without accepting the root')
parser.add_argument('--owner-root-accepted', action='store_true', help='Observe actual control flow after the explicit independent owner root enforcement')
parser.add_argument('--inspect-owner-root', action='store_true', help='Capture actual root policy state at the selected later checkpoint')
parser.add_argument('--inspect-compression', action='store_true', help='Capture actual original type-3/type-4 decompressor registrations')
parser.add_argument('--inspect-dyld-flags', action='store_true', help='Capture actual kernel and commpage startup flags after owner verification')
parser.add_argument('--skip-policy-pointer-reads', action='store_true', help='Observe pre-allocation refusal using raw integrity pointer globals, without dereferencing null')
parser.add_argument('--verified-root-probe', action='store_true', help='Run the opt-in genuine XNU owner-signature crypto instrument; no root-policy fallback')
parser.add_argument('--inspect-entry-translations', action='store_true', help='Inspect actual native PTEs for original function arguments after its return')
parser.add_argument('--finish-function', action='store_true')
parser.add_argument('--exercise-ufs-allocation', action='store_true',
                    help='Offline debugger-invoked actual XNU allocation/translation qualification, without UFS MMIO')
parser.add_argument('--entry-kernel-bytes-field', help='Select a real finished function by ARG:HEX_OFFSET:HEX_BYTES in kernel memory')
parser.add_argument('--entry-process-name', help='Bounded observer selection by actual compiler-qualified current process name')
parser.add_argument('--entry-min-pid',type=int,default=0,help='Minimum actual PID for an explicitly named process predicate')
parser.add_argument('--entry-register-equals', help='Observe the call whose actual ARG equals HEX_VALUE')
parser.add_argument('--entry-max-skips', type=int, default=16, help='Bound real kernel-byte identity selection to at most 65536 skipped calls')
parser.add_argument('--read-entry-region', action='append', default=[], help='Read an actual bounded kernel argument region ARG:HEX_OFFSET:HEX_LENGTH at entry or after return')
parser.add_argument('--read-saved-user-register',action='append',default=[],help='Read bounded memory through a register from the actual saved user state')
parser.add_argument('--inspect-entry-user-state', action='store_true', help='Read bounded callee-saved kernel pointers for ABI-qualified user saved-state candidates at the actual entry')
parser.add_argument('--read-frame-locals', action='store_true', help='Read at most 192 bytes below each of at most 16 actual kernel frame pointers')
parser.add_argument('--read-frame-indirect', action='append', default=[], help='Read kernel memory through a real saved frame slot FRAME:SIGNED_HEX_OFFSET:HEX_LENGTH')
parser.add_argument('--entry-user-string-field', help='Select a real finished function call by ARG:HEX_OFFSET:VALUE in a user string pointer field')
parser.add_argument('--read-entry-indirect', action='append', default=[], metavar='ARG:OFFSET:LENGTH', help='Read an actual entry argument pointer field through the existing bounded observer')
parser.add_argument('--read-entry-user-vector', action='append', default=[], help='Read an actual bounded user argv vector through ARG:HEX_OFFSET:HEX_COUNT')
parser.add_argument('--read-entry-user-indirect', action='append', default=[], metavar='ARG:OFFSET:LENGTH', help='Read an explicitly user-space pointer field through the bounded observer')
parser.add_argument('--negative-platform-match', action='store_true', help='Supply an explicit unmatched synthetic platform compatible string')
parser.add_argument('--smp', type=int, default=1, help='Offline QEMU CPU count; above 1 enables sheng-smp and the PSCI secondary-start path')
parser.add_argument('--armcpu', action='store_true', help='Describe GICv3 resources and inspect real CPU/IRQ initialization')
parser.add_argument('--missing-gic', action='store_true', help='Omit GIC resources to test CPU driver rejection')
parser.add_argument('--check-commpage', action='store_true', help='Require real legacy and RO commpage user page shifts of 12')
parser.add_argument('--native-user', action='store_true', help='Boot the signed static Darwin EL0/SVC fixture as md0/mockfs')
parser.add_argument('--native-data-user-image',type=Path,help='Observe a fixed-address own static instrument staged through the signed original-root/Data init path; no mockfs boot')
parser.add_argument('--native-user-image', type=Path, help='Explicit own process image with a sibling addresses.json symbol record')
parser.add_argument('--data-ramdisk', type=Path, help='Explicit mutable scratch APFS initrd; retain the genuine original OS disk root')
parser.add_argument('--native-user-ramdisk', type=Path, help='Explicit two-file offline root; own process symbols remain separate')
parser.add_argument('--mutate-own-ramdisk-after-auth', type=lambda value: int(value, 0),
                    help='Offline TOCTOU refusal test: XOR this own md0 byte after full-block authentication')
parser.add_argument('--mutate-own-vnode-page', type=lambda value: int(value, 0),
                    help='Offline integrity refusal test: XOR this own file byte in its actual faulting VM page')
parser.add_argument('--mutate-cache-vnode-page', type=lambda value: int(value, 0),
                    help='Offline APFS integrity refusal: XOR one original cache byte only in its actual faulting VM page')
parser.add_argument('--cache-page-source', type=Path, help='Exact unchanged supplied arm64.02 file identifying the cache fault input')
parser.add_argument('--skip-initializer-traces', action='store_true', help='Keep initializer state inspection but omit their one-shot breakpoints when the accelerator has a hardware breakpoint limit')
parser.add_argument('--trace-symbol', action='append', default=[], help='Record a one-shot kernel milestone within the same bounded VM run')
parser.add_argument('--kext-logs', action='store_true', help='Capture bounded real OSKext error/warning calls')
parser.add_argument('--nvram-proxy', action='store_true', help='Supply an empty volatile CHRP snapshot to the real IODTNVRAM service')
parser.add_argument('--conflicting-boot-manifest', action='store_true', help='Isolated offline refusal control: supply an untrusted existing identity that owner verification must not overwrite')
parser.add_argument('--crypto-hash-method', choices=['sha2-384', 'sha1'], help='Set an explicit Image4 hash algorithm in the QEMU DT')
parser.add_argument('--osenvironment', choices=['ramdisk','recoveryos','main'], help='Set a real /chosen/osenvironment fixture; not a hardware observation')
parser.add_argument('--kernel-extra-args', default='', help='Append explicit offline kernel boot arguments; characters are restricted')
parser.add_argument('--amfi-platform-only', action='store_true', help='Require platform code in the offline AMFI policy fixture')
parser.add_argument('--trust-cache', type=Path, help='Explicit XNU offset-table/version-2 module bundle for owned loader handoff')
parser.add_argument('--prelink-report', type=Path, help='Require crypto registration from the exact original-component candidate')
parser.add_argument('--load-apfs', action='store_true', help='Offline debug probe: request genuine APFS kext loading after VFS initialization')
parser.add_argument('--load-iogpu', action='store_true', help='Explicit offline original IOGPUFamily load request; no hardware GPU service')
parser.add_argument('--load-hid-input',action='store_true',help='Observe supplied original IOHIDFamily initialization after genuine IOBSD publication')
parser.add_argument('--hid-home-input',action='store_true',help='Enable an explicit offline source for Consumer Menu press/release through the original HID parser')
parser.add_argument('--live-hid-dir',type=Path,help='Own input command/status directory for the live QEMU instance')
parser.add_argument('--load-mobile-graphics', action='store_true', help='Explicit offline debug request for genuine original IOMobileGraphicsFamily loading; no framebuffer service is supplied')
parser.add_argument('--constant-uploads-probe', action='store_true', help='Run the explicitly built native parameter packer/refusal fixture; no GPU access')
parser.add_argument('--inspect-constant-uploads', action='store_true', help='Read actual parameter bytes and native 4K allocation/guard mappings at its checkpoint')
parser.add_argument('--smmu4k-probe', action='store_true', help='Run the explicitly built inactive native table/allocation fixture; no SMMU activation')
parser.add_argument('--inspect-smmu4k', action='store_true', help='Capture actual allocated inactive tables/data and every active CPU mapping')
parser.add_argument('--adreno-pm4-probe', action='store_true', help='Run the explicitly built offline native PM4 structure/refusal controls; no GPU access')
parser.add_argument('--adreno-firmware-probe', action='store_true', help='Run the explicitly built offline native GMU planner/hash controls; no GPU access')
parser.add_argument('--inspect-adreno-firmware', action='store_true', help='Read actual native GMU planner state and its constant input pointer')
parser.add_argument('--mobile-graphics-client-probe', action='store_true', help='Explicit offline original class allocation and out-of-range selector refusal checks; requires --load-mobile-graphics')
parser.add_argument('--legacy-display-phase', type=int, choices=[1,2,3,4], help='Explicit compiled Legacy lifecycle: init, GOP-resource start, own transfer service, or guarded original-client experiment')
parser.add_argument('--legacy-display-gop', action='store_true', help='Enable the explicit offline original Legacy GOP mapping backend')
parser.add_argument('--legacy-display-transfer',action='store_true',help='Bounded first validated GPU frame to actual GOP; retain original queue ownership, no invented completion')
parser.add_argument('--original-cpu-present',action='store_true',help='Offline original synchronous software-renderer experiment: retire only after actual validated scanout copy')
parser.add_argument('--legacy-display-retire',action='store_true',help='After actual first-frame transfer, use original pending-request completion and waiter wakeup')
parser.add_argument('--offline-gpu-broker',action='store_true',help='Publish only the explicit private GPU broker for the owned native instrument')
parser.add_argument('--accelerator-abi-probe',action='store_true',help='Construct/free an unpublished own object through the original accelerator base; no normal GPU publication')
parser.add_argument('--original-client-abi-probe',action='store_true',help='Allocate/free the real registered original IOGPU userclient and observe a wrong-provider refusal; no client publication')
parser.add_argument('--original-provider-probe',choices=['lifecycle','start','client-factory','client-refusal','descriptor-provision','descriptor-provision-attached','descriptor-provision-attached-only'],help='Unpublished original IOGPU lifecycle/start/client-factory/descriptor-availability observation')
parser.add_argument('--original-provider-client-type',type=lambda value:int(value,0),default=1,help='Actual original factory open type for the explicit client-factory instrument')
parser.add_argument('--legacy-display-validate',action='store_true',help='Explicit original request validation for one actual full-frame nonplanar BGRA IOSurface')
parser.add_argument('--legacy-display-logical-pm',action='store_true',help='Explicit offline IOKit logical scanout scheduling lifecycle; no panel power capability')
parser.add_argument('--legacy-display-unit-scale',action='store_true',help='Explicit actual GOP one-logical-pixel-per-pixel policy via original chosen display-scale metadata')
parser.add_argument('--legacy-display-register',action='store_true',help='Explicit offline GOP-backed original client discovery experiment; unknown calls still stop')
parser.add_argument('--legacy-display-register-only',action='store_true',help='Register the GOP display without the explicit probe client; observe system processes only')
parser.add_argument('--inspect-gop-scanout-bytes',type=lambda s:int(s,0),help='Expected actual GOP extent, up to 4 MiB; inspect every active CPU mapping page')
parser.add_argument('--trace-mobile-graphics-factories', action='store_true', help='Observe the three actual abstract factories instead of kmod/request entry, within HVF breakpoint limits')
block_group = parser.add_mutually_exclusive_group()
block_group.add_argument('--virtio-block-image', type=Path, help='Raw file for strictly read-only actual MMIO block I/O')
block_group.add_argument('--virtio-udif-image', type=Path, help='Already attached read-only UDIF image, verified against actual host virtual media')
parser.add_argument('--virtio-extra-block-image', type=Path, help='Second existing read-only raw volume for offline component tests')
parser.add_argument('--log-registry-strings', action='store_true', help='Observe actual IOMedia UUID/BSD names without assuming disk enumeration')
root_group = parser.add_mutually_exclusive_group()
root_group.add_argument('--root-volume-uuid', type=uuid.UUID, help='Actual image volume UUID for genuine boot-volume matching')
root_group.add_argument('--root-bsd-name', help='Previously observed actual IOMedia BSD name for genuine root selection')
root_group.add_argument('--root-match-volume-uuid', type=uuid.UUID, help='Select a real volume UUID with standard DT IOMedia root-matching')
parser.add_argument('--virtio-mmio-fdt', type=Path, help='Actual QEMU-generated FDT describing the corresponding resource windows')
parser.add_argument('--missing-virtio-device', action='store_true', help='Actual empty-MMIO-window refusal control')
parser.add_argument('--boot-progress-clock-fixture', type=int, choices=(31,121),
                    help='QEMU-only: advance own diagnostic epoch at its first poll; no OS/timebase/register mutation')
args = parser.parse_args()
if args.qemu_ramfb_high_resolution:
    if not args.qemu_ramfb:
        parser.error('High-resolution fixture requires the actual QEMU ramfb')
    args.inspect_boot_video = True
    args.capture_qemu_screen = True
if args.timeout>300 and not args.live_hid_dir:parser.error('Deadlines above 300 seconds require explicit live HID control')
if args.inspect_ui_threads:
    args.inspect_current_process = True
    args.inspect_process_list = True
if args.boot_progress_clock_fixture:
    if args.break_symbol != '_boot_progress_stop_checkpoint' or args.qemu_accel != 'tcg':
        parser.error('Clock fixture requires TCG and the diagnostic stop checkpoint')
    args.trace_symbol.append('_boot_progress_poll')
data_seed = None
if args.data_ramdisk:
    if args.native_user or not args.prelink_report or not args.root_match_volume_uuid:
        parser.error('Scratch Data requires the exact original OS root/prelink path')
    import sys
    sys.path.insert(0, str(ROOT / 'drivers/DarwinBoot/Test'))
    from packed_ramdisk import inspect as inspect_ramdisk
    try:
        data_seed, data_header = inspect_ramdisk(args.data_ramdisk)
    except ValueError as error:
        parser.error(str(error))
    if data_header[32:36] != b'NXSB':
        parser.error('Scratch Data must expand to an actual raw APFS container')
    data_seed.update(guest_mutable=True, production_storage_qualified=False,
                     initial_seed_signature_verified=False)

main_fault = args.mutate_target_main_page
if main_fault and (not args.follow_target_main or args.mutate_own_vnode_page is not None or args.mutate_cache_vnode_page is not None or args.mutate_own_ramdisk_after_auth is not None):
    parser.error('Original main-page fault requires its exact main observer and no other input fault')
main_input = None
display_plan = None
process_plan = None
if args.follow_original_user_plan:
    if not args.follow_target_main or any((args.follow_display_mode,args.follow_metal_device,args.follow_display_query,args.follow_display_discovery)):
        parser.error('Original user plan requires original launchd main and no other display observer')
    display_plan=args.follow_original_user_plan
    selected_plan=json.loads(display_plan.read_text())
    if selected_plan.get('mode') not in ('user-return','user-trace') or selected_plan.get('original_files_modified') is not False:
        parser.error('Require a read-only original user-return or user-trace plan')
if args.entry_process_name and not args.inspect_current_process:parser.error('Process-name selection requires --inspect-current-process')
if args.inspect_current_process:
    if not args.prelink_report:
        parser.error('Process inspection requires the exact original-component candidate')
    subprocess.run(['python3', ROOT / 'scripts/audit-target-display-query.py'], check=True)
    process_plan = ROOT / 'build/display-analysis/query-plan.json'
if args.follow_display_mode or args.follow_metal_device:
    if not args.follow_target_main or args.follow_display_query or args.follow_display_discovery or (args.follow_display_mode and args.follow_metal_device):parser.error('Mode return requires original main and no other display observer')
    subprocess.run(['python3',ROOT/'scripts/prepare-original-display-mode-observer.py',*(['--metal-device'] if args.follow_metal_device else [])],check=True)
    display_plan=ROOT/('build/display-analysis/metal-device-return-plan.json' if args.follow_metal_device else 'build/display-analysis/mode-plan.json')
if args.follow_display_query or args.follow_display_discovery:
    if not args.follow_target_main:
        parser.error('Display query observation requires actual original launchd main')
    if args.follow_display_query and args.follow_display_discovery:
        parser.error('Select one original display observation')
    subprocess.run(['python3', ROOT / 'scripts/audit-target-display-query.py', *(['--discovery'] if args.follow_display_discovery else [])], check=True)
    display_plan = ROOT / ('build/display-analysis/discovery-plan.json' if args.follow_display_discovery else 'build/display-analysis/query-plan.json')
if args.native_air_init and args.follow_target_main:
    parser.error('Own compiler init and original launchd main are distinct observations')
if args.follow_target_main:
    if args.native_user or args.finish_function or args.break_symbol != '_panic' or args.break_address is not None or not args.prelink_report:
        parser.error('Original main observation requires its exact original-component candidate and genuine OS root, without another checkpoint')
    main_bytes = (args.target_main_executable or ROOT / '.cache/firmware/target-volumes/os-mount/sbin/launchd').read_bytes()
    if hashlib.sha256(main_bytes).hexdigest() != '8cec9a3c44a443b08e977ccc5d577850316ad428c575dc01f09b018dbd5b6a25':
        raise SystemExit('Expected the unchanged supplied original launchd')
    sys.path.insert(0, str(ROOT / 'kits/XnuPrelink'))
    from native_prelink import macho
    main_image = macho(main_bytes)
    entries = [struct.unpack_from('<Q', main_bytes, at + 8)[0] for cmd, at, size in main_image['commands'] if cmd == 0x80000028]
    text = [s for s in main_image['segments'] if s['name'] == '__TEXT' and s['fileoff'] == 0]
    if len(entries) != 1 or len(text) != 1 or not 0 < entries[0] < text[0]['filesize'] - 16:
        raise SystemExit('Require one backed LC_MAIN relative to the main Mach header')
    main_input = dict(sha256=hashlib.sha256(main_bytes).hexdigest(), entry_offset=entries[0],
        entry_prefix=main_bytes[entries[0]:entries[0] + 16].hex(), mach_header=main_bytes[:32].hex())
    args.break_symbol = '_thread_setentrypoint'
if args.follow_cache_leaf and (not args.native_user or not args.native_user_image or args.finish_function or args.break_symbol != '_panic'):
    parser.error('The cache-code return probe requires its explicit own process and no alternate stop request')
if args.owner_root_audit and args.owner_root_accepted:
    parser.error('Select either the before-enforcement audit or the actual post-enforcement checkpoint')
if (args.owner_root_audit or args.owner_root_accepted) and (not args.prelink_report or args.native_user or args.break_symbol != '_panic'):
    parser.error('The root audit requires its exact original-component kernel and an actual disk root')
if args.owner_root_audit:
    args.break_symbol = '_native_owner_root_checkpoint'
if args.owner_root_accepted:
    args.break_symbol = '_native_owner_root_accepted_checkpoint'
if args.verified_root_probe and (not args.prelink_report or args.native_user or args.break_symbol != '_panic'):
    parser.error('The owner-crypto probe requires its exact native candidate and its own kernel checkpoint')
if args.verified_root_probe:
    args.break_symbol = '_native_verified_root_checkpoint'
if args.inspect_entry_translations and not (args.finish_function or args.follow_cache_leaf or args.inspect_compression or args.inspect_adreno_firmware):
    parser.error('Translation inspection requires an actual function return or explicitly captured kernel pointers')
prelink_report = None
if args.prelink_report:
    prelink_report = json.loads(args.prelink_report.read_text())
    if hashlib.sha256(args.kernel.read_bytes()).hexdigest() != prelink_report['candidate_sha256']:
        raise SystemExit('Prelink report does not identify this exact candidate')
if args.break_address is not None:
    if (not prelink_report or args.break_symbol != '_panic' or
            not any(e['segment'] == '__TEXT_EXEC' and e['va'] <= args.break_address < e['va'] + e['size']
                    for e in prelink_report['extents'])):
        parser.error('An original address requires its exact component text extent and no symbol override')
    args.break_symbol = 'original-component-address'
block_image = args.virtio_block_image or args.virtio_udif_image
if (args.root_volume_uuid or args.root_bsd_name or args.root_match_volume_uuid) and (not block_image or args.native_user):
    parser.error('Root UUID selection requires a real offline disk and conflicts with the md0 root')
if args.root_bsd_name and not re.fullmatch(r'disk[0-9]+(?:s[0-9]+)*', args.root_bsd_name):
    parser.error('Expected an actual disk BSD name')
if args.load_apfs and not args.prelink_report:
    parser.error('--load-apfs requires an explicit original-component candidate report')
if args.load_mobile_graphics and not args.prelink_report:
    parser.error('--load-mobile-graphics requires an exact original-component candidate report')
if (args.adreno_firmware_probe or args.adreno_pm4_probe or args.load_iogpu or args.smmu4k_probe or args.inspect_smmu4k or args.constant_uploads_probe or args.inspect_constant_uploads) and not args.prelink_report:
    parser.error('GPU diagnostics require an exact original-component candidate report')
if args.inspect_constant_uploads and (not args.constant_uploads_probe or args.break_symbol != '_native_constants_checkpoint'):
    parser.error('Constant inspection requires its enabled live checkpoint')
if args.inspect_constant_uploads and args.inspect_smmu4k:
    parser.error('Inspect constants and SMMU allocations in separate bounded runs')
if args.inspect_smmu4k and not args.smmu4k_probe:
    parser.error('Allocated table inspection requires the enabled native SMMU4K fixture')
if args.mobile_graphics_client_probe and not args.load_mobile_graphics:
    parser.error('--mobile-graphics-client-probe requires --load-mobile-graphics')
if args.trace_mobile_graphics_factories and not args.mobile_graphics_client_probe:
    parser.error('--trace-mobile-graphics-factories requires --mobile-graphics-client-probe')
if args.load_apfs and args.break_symbol == '_panic' and not args.inspect_owner_root:
    args.break_symbol = '_native_apfs_probe_checkpoint'
if bool(block_image) != bool(args.virtio_mmio_fdt) or (block_image and not args.armvirt):
    parser.error('The block test requires both a raw image and actual MMIO FDT, with --armvirt')
if block_image and args.break_symbol == '_panic' and not args.inspect_owner_root:
    args.break_symbol = '_native_virtio_read_checkpoint'
if args.virtio_extra_block_image and (not block_image or args.missing_virtio_device):
    parser.error('A second raw volume requires the first real attached offline disk')
if args.missing_virtio_device and not block_image:
    parser.error('--missing-virtio-device requires the explicit block test input')
if args.native_user and not args.armcpu:
    parser.error('--native-user requires --armcpu')
if args.native_data_user_image and (args.native_user or not args.native_air_init or not args.data_ramdisk or not args.inspect_owner_root):
    parser.error('Static Data observation requires its signed original-root/Data init instrument, without mockfs')
if args.native_user_image and not args.native_user:
    parser.error('--native-user-image requires --native-user')
if args.native_user_ramdisk and (not args.native_user or not args.native_user_image):
    parser.error('--native-user-ramdisk requires --native-user and its explicit own process image')
if args.native_user_ramdisk and (args.mutate_own_ramdisk_after_auth is not None or args.mutate_own_vnode_page is not None):
    parser.error('Single-file mutation hooks do not identify a two-file root')
if args.mutate_own_ramdisk_after_auth is not None and not args.native_user:
    parser.error('--mutate-own-ramdisk-after-auth requires the own native-user fixture')
if args.mutate_own_vnode_page is not None and not args.native_user:
    parser.error('--mutate-own-vnode-page requires the own native-user fixture')
cache_fault = args.mutate_cache_vnode_page is not None
if cache_fault != bool(args.cache_page_source) or (cache_fault and
        (not args.native_user_image or not block_image or args.mutate_own_vnode_page is not None)):
    parser.error('Cache page fault requires its exact original source, explicit own process and real offline disk')
if args.missing_gic and not args.armcpu:
    parser.error('--missing-gic requires --armcpu')
if args.qemu_accel == 'hvf' and not (args.armvirt and args.qemu_vmm_present):
    parser.error('HVF requires the actual QEMU platform and explicit VMM identity')
output = args.output.resolve()
esp = output / 'esp'
payloads = esp / 'EFI/UniXNU/Payloads'
payloads.mkdir(parents=True, exist_ok=True)
(esp / 'EFI/BOOT').mkdir(exist_ok=True)
subprocess.run(['python3', ROOT / 'scripts/audit-xnu-kernel.py', args.kernel], check=True)
shutil.copyfile(output_dir(ROOT) / 'UniXNU.efi', esp / 'EFI/BOOT/BOOTAA64.EFI')
shutil.copyfile(ROOT / 'build/DarwinBoot/DEBUG_CLANGPDB/AARCH64/DarwinBoot.efi', payloads / 'DarwinBoot.efi')
shutil.copyfile(args.kernel, payloads / 'kernel.macho')
trust_sidecar = payloads / 'kernel.macho.trustcache'
if args.trust_cache:
    shutil.copyfile(args.trust_cache, trust_sidecar)
else:
    trust_sidecar.unlink(missing_ok=True)
dt_command = ['python3', ROOT / 'scripts/qemu-entry/make-dt.py', '--output',
              payloads / 'kernel.macho.adt', '--dram-size', str(args.qemu_memory_mib * 1024**2), '--qemu-accel', args.qemu_accel]
if args.owned_memory_size is not None:
    dt_command += ['--owned-memory-size', str(args.owned_memory_size)]
if args.qemu_vmm_present:
    if not args.armvirt:
        parser.error('--qemu-vmm-present requires --armvirt')
    dt_command.append('--qemu-vmm-present')
if args.armvirt:
    dt_command.append('--armvirt')
if args.armdt_platform:
    if not args.armvirt:
        parser.error('--armdt-platform requires --armvirt for actual offline GIC resources')
    dt_command.extend(['--platform-compatible', 'xiaomi,sheng'])
if args.armcpu:
    if not args.armvirt:
        parser.error('--armcpu requires --armvirt')
    if not args.missing_gic:
        dt_command.append('--armcpu')
    if args.smp > 1:
        dt_command += ['--smp', str(args.smp)]
if args.negative_platform_match:
    if not args.armvirt:
        parser.error('--negative-platform-match requires --armvirt')
    dt_command.extend(['--platform-compatible', 'unmatched-test-platform'])
if args.armdt_platform and args.negative_platform_match:
    parser.error('Select either the sheng-shaped root or the unmatched control')
if args.native_user:
    dt_command.append('--ramdisk')
if args.data_ramdisk:
    dt_command.append('--data-ramdisk')
if args.nvram_proxy:
    dt_command.append('--nvram-proxy')
if args.conflicting_boot_manifest:
    if not args.prelink_report or args.native_user:
        parser.error('Manifest conflict control requires the original OS prelink path')
    dt_command.append('--conflicting-boot-manifest')
if args.crypto_hash_method:
    dt_command.extend(['--crypto-hash-method', args.crypto_hash_method])
if args.osenvironment:
    dt_command.extend(['--osenvironment', args.osenvironment])
if args.amfi_platform_only:
    dt_command.append('--amfi-platform-only')
if args.trust_cache:
    dt_command.append('--trust-cache')
if args.virtio_mmio_fdt:
    dt_command += ['--virtio-mmio-fdt', args.virtio_mmio_fdt]
if args.root_match_volume_uuid:
    dt_command += ['--root-match-volume-uuid', str(args.root_match_volume_uuid)]
subprocess.run(dt_command, check=True)
import re as _re
if not _re.fullmatch(r'[A-Za-z0-9_=. +\-]*', args.kernel_extra_args):
    raise SystemExit('Kernel extra arguments contain unsupported characters')
kernel_args = ('-v serial=3 debug=0x14e kt_fixed_zones=120 ' + args.kernel_extra_args).strip()
(esp / 'EFI/UniXNU/unixnu.toml').write_text(f'''version = 1
[boot]
timeout = 1
default = "source-4k"
[kits]
autoload = false
[[driver]]
path = "Payloads/DarwinBoot.efi"
[[entry]]
id = "source-4k"
title = "Source native 4K XNU"
type = "xnu"
path = "Payloads/kernel.macho"
args = "{kernel_args}"
''')
user_addresses = None
if args.qemu_ramfb_high_resolution:
    if not args.qemu_ramfb:
        parser.error('High-resolution fixture requires the actual QEMU ramfb')
    driver = ROOT / 'build/DarwinBoot/DEBUG_CLANGPDB/AARCH64/QemuRamfbGeometry.efi'
    shutil.copyfile(driver, payloads / driver.name)
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('[[entry]]',
        '[[driver]]\npath = "Payloads/QemuRamfbGeometry.efi"\n[[entry]]', 1))
if args.native_user:
    user_directory = args.native_user_image.parent if args.native_user_image else ROOT / 'build/native-user-fixture'
    shutil.copyfile(args.native_user_image or user_directory / 'launchd.macho', payloads / 'launchd.macho')
    user_addresses = json.loads((user_directory / 'addresses.json').read_text())
    root_name = 'launchd.macho'
    if args.native_user_ramdisk:
        root_name = 'root.img'
        shutil.copyfile(args.native_user_ramdisk, payloads / root_name)
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "-v', f'initrd = "Payloads/{root_name}"\nargs = "rd=md0 -v'))
    if args.break_symbol == '_panic':
        args.break_symbol = '_native_user_checkpoint'
if args.data_ramdisk:
    shutil.copyfile(args.data_ramdisk, payloads / 'scratch-data.img')
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "-v', 'initrd = "Payloads/scratch-data.img"\nargs = "-v'))
if args.verified_root_probe:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-owner-root-check=1 ', 1))
if args.load_apfs:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-apfs-load=1 ', 1))
if args.load_iogpu:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-iogpu-load=1 ', 1))
if args.load_mobile_graphics:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-mobile-graphics-load=1 ', 1))
if args.native_air_init:
    if not args.data_ramdisk or not args.trust_cache or not args.inspect_owner_root:
        parser.error('Offline AIR init requires explicit Data, trust bundle and real owner-root checks')
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-air-init=1 ', 1))
if args.offline_gpu_broker:
    if not args.native_air_init:parser.error('Private GPU broker requires the explicit owned diagnostic')
    config.write_text(config.read_text().replace('args = "','args = "offline-gpu-broker=1 ',1))
if args.accelerator_abi_probe:
    if not args.offline_gpu_broker:parser.error('Accelerator ABI observation requires the explicit private broker startup boundary')
    config.write_text(config.read_text().replace('args = "','args = "offline-accelerator-abi=1 ',1))
if args.original_client_abi_probe:
    if not args.offline_gpu_broker:parser.error('Original client ABI observation requires the explicit private broker lifecycle hook')
    config.write_text(config.read_text().replace('args = "','args = "offline-original-client-abi=1 ',1))
if args.original_provider_probe:
    if not args.offline_gpu_broker:parser.error('Provider ABI observation requires the explicit private backend hook')
    if not 0<=args.original_provider_client_type<=0xffffffff:parser.error('Original client type must fit uint32')
    mode={'lifecycle':1,'start':2,'client-factory':3,'client-refusal':4,'descriptor-provision':5,'descriptor-provision-attached':6,'descriptor-provision-attached-only':7}[args.original_provider_probe]
    config.write_text(config.read_text().replace('args = "','args = "offline-original-provider-abi='+str(mode)+' offline-original-client-type='+str(args.original_provider_client_type)+' ',1))
if args.constant_uploads_probe:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-constants=1 ', 1))
if args.smmu4k_probe:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-smmu4k=1 ', 1))
if args.adreno_pm4_probe:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-adreno-pm4=1 ', 1))
if args.adreno_firmware_probe:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-adreno-firmware=1 ', 1))
if args.mobile_graphics_client_probe:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', 'args = "offline-mobile-graphics-client=1 ', 1))
if args.legacy_display_phase:
    if not args.mobile_graphics_client_probe:parser.error('Legacy lifecycle requires the explicit original-family client gate')
    config.write_text(config.read_text().replace('args = "', f'args = "offline-legacy-phase={args.legacy_display_phase} ', 1))
if args.live_hid_dir and not args.hid_home_input:parser.error('Live HID requires the explicit offline input source')
if args.hid_home_input and not args.load_hid_input:
    parser.error('Offline Home report requires original HID loading')
if args.load_hid_input:
    if not (args.load_mobile_graphics and args.prelink_report and args.legacy_display_phase==4):
        parser.error('HID observation requires the original system/display late-init experiment')
    config=esp/'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "','args = "offline-hid-input=1 ',1))
    if args.hid_home_input:config.write_text(config.read_text().replace('args = "','args = "offline-hid-home=1 ',1))
if args.smp > 1:
    if not args.armcpu:
        parser.error('--smp requires --armcpu')
    config=esp/'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "','args = "sheng-smp=1 ',1))
if args.original_cpu_present:
    if not (args.legacy_display_transfer and args.load_mobile_graphics and args.prelink_report) or args.native_air_init or args.native_user:
        parser.error('Original CPU presentation requires original system graphics and validated copy, without an owned renderer')
    config=esp/'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "','args = "offline-legacy-cpu-present=1 ',1))
if args.legacy_display_retire:
    if not (args.legacy_display_transfer and args.native_air_init):parser.error('Original retirement requires actual validated GOP transfer and the explicit owned diagnostic')
    config=esp/'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "','args = "offline-legacy-retire=1 ',1))
if args.legacy_display_transfer:
    if not args.legacy_display_validate:parser.error('Bounded GOP transfer requires actual original surface validation')
    config=esp/'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "','args = "offline-legacy-transfer=1 ',1))
if args.legacy_display_validate:
    if not args.legacy_display_logical_pm:parser.error('Original full-frame validation requires logical scanout scheduling')
    config=esp/'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "','args = "offline-legacy-validate=1 ',1))
if args.legacy_display_logical_pm:
    if not (args.legacy_display_gop and args.legacy_display_register and args.legacy_display_phase==4):parser.error('Logical scanout PM requires the explicit GOP phase-4 experiment')
    config=esp/'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "','args = "offline-legacy-pm=1 ',1))
if args.legacy_display_unit_scale:
    config=esp/'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = \"','args = \"offline-legacy-unit-scale=1 ',1))
if args.legacy_display_gop:
    if args.legacy_display_phase not in (2,4):parser.error('Legacy GOP backend requires the explicit start phase')
    config.write_text(config.read_text().replace('args = "', 'args = "offline-legacy-gop=1 ', 1))
if args.legacy_display_unit_scale and not (args.legacy_display_gop and args.legacy_display_register and args.legacy_display_phase==4):parser.error('Unit-scale policy requires the actual GOP-backed phase-4 system experiment')
if args.legacy_display_register:
    if args.legacy_display_phase!=4 or not args.legacy_display_gop:parser.error('Original client experiment requires explicit phase 4 and genuine GOP backend')
    config.write_text(config.read_text().replace('args = "','args = "offline-legacy-register=1 ',1))
if args.legacy_display_register_only:
    if not args.qemu_ramfb:parser.error('Register-only display needs the actual GOP ramfb')
    config.write_text(config.read_text().replace('args = "','args = "offline-mobile-graphics-load=1 offline-legacy-gop=1 offline-legacy-phase=4 offline-legacy-register=1 ',1))
if args.root_volume_uuid:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', f'args = "rd=uuid boot-uuid={str(args.root_volume_uuid).upper()} ', 1))
if args.root_bsd_name:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', f'args = "rd={args.root_bsd_name} ', 1))
if args.zone_pgz_probe_case:
    config = esp / 'EFI/UniXNU/unixnu.toml'
    config.write_text(config.read_text().replace('args = "', f'args = "offline-zone-pgz-case={args.zone_pgz_probe_case} ', 1))
if args.native_data_user_image:
    user_addresses=json.loads((args.native_data_user_image.parent/'addresses.json').read_text())
    args.native_user=True # Observation only; ESP already retains the original OS and actual Data.
symbols = subprocess.check_output(['xcrun', 'nm', '-U', args.kernel], text=True)
panic = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + re.escape(args.break_symbol) + '$', symbols, re.M)
if args.break_address is not None:
    panic = {1: f'{args.break_address:x}'}
if args.follow_cache_leaf:
    leaf_record = json.loads((args.native_user_image.parent / 'cache-leaf.json').read_text())
    if hashlib.sha256(args.native_user_image.read_bytes()).hexdigest() != leaf_record['own_process_sha256']:
        raise SystemExit('Cache-code fixture identity mismatch')
    args.break_symbol = '_original_cache_leaf_return'
    panic = {1: f"{user_addresses['_cache_leaf_dispatch']:x}"}
elif args.native_user and args.break_symbol == '_native_user_checkpoint':
    panic = {1: f"{user_addresses['_checkpoint']:x}"}
if not panic:
    raise SystemExit(f'Cannot resolve {args.break_symbol} in this kernel')
page_globals = {}
compression_requests = {}
if args.inspect_process_list:
    match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+_allproc$', symbols, re.M)
    if not match:
        raise SystemExit('Cannot resolve the actual kernel allproc list')
    process_list_args = ['--allproc-address', '0x' + match[1],
                         '--proc-list-offset', '0', '--proc-pid-offset', '96',
                         '--proc-comm-offset', '1468', '--proc-stat-offset', '100']
else:
    process_list_args = []
gdb_command = ['python3', ROOT / 'scripts/qemu-entry/gdb-stop.py', f'0x{panic[1]}',
               '--fixture', output, '--esp', esp, '--kernel', args.kernel,
               '--system-registers', '--timeout', str(args.timeout), '--qemu-accel', args.qemu_accel,
               '--qemu-memory-mib', str(args.qemu_memory_mib)]
gdb_command += process_list_args
if args.capture_scratch_data:
    if not args.data_ramdisk:
        parser.error('Scratch Data capture requires an actual Data RAM disk input')
    pointers = []
    for name in ('_native_owner_data_seed_base', '_native_owner_data_seed_size'):
        match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + name + '$', symbols, re.M)
        if not match:
            raise SystemExit('Missing exact native Data capture symbol: ' + name)
        pointers.append(match[1])
    gdb_command += ['--capture-scratch-data', ':'.join(pointers + [f'{data_seed["bytes"]:x}'])]
if args.inspect_ui_threads:
    gdb_command += ['--proc-list-max', '512']
if args.boot_progress_clock_fixture:
    addresses=[]
    for name in ('_boot_progress_poll','_boot_progress_epoch','_boot_progress_frequency'):
        match=re.search(r'^([0-9a-fA-F]+)\s+\S\s+'+name+'$',symbols,re.M)
        if not match:raise SystemExit('Missing diagnostic-only clock symbol '+name)
        addresses.append(match[1])
    gdb_command += ['--boot-progress-clock-fixture',':'.join(addresses+[str(args.boot_progress_clock_fixture)])]
if args.exercise_ufs_allocation:
    gdb_command += ['--exercise-ufs-allocation']
if args.inspect_mac_policies:
    objects=ROOT/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/security/DEVELOPMENT'
    layout={};dwarf={}
    for structure,obj,names in (
        ('mac_policy_list','mac_base.o',('numloaded','max','maxindex','staticmax','entries')),
        ('mac_policy_list_element','mac_base.o',('mpc',)),
        ('mac_policy_conf','mac_vfs.o',('mpc_name','mpc_fullname','mpc_ops')),
        ('mac_policy_ops','mac_vfs.o',('mpo_proc_check_fork','mpo_vnode_check_exec','mpo_vnode_check_signature','mpo_proc_check_launch_constraints','mpo_file_check_mmap','mpo_policy_syscall'))):
        text=subprocess.check_output(['xcrun','dwarfdump','--name='+structure,'--show-children',objects/obj],text=True)
        dwarf[obj]=hashlib.sha256((objects/obj).read_bytes()).hexdigest();layout[structure]={}
        for name in names:
            match=re.search(r'DW_AT_name\s+\("'+name+r'"\)[\s\S]*?DW_AT_data_member_location\s+\((0x[0-9a-f]+)\)',text)
            if not match:raise SystemExit('Cannot qualify actual MAC policy member '+name)
            layout[structure][name]=int(match[1],16)
    match=re.search(r'^([0-9a-fA-F]+)\s+\S\s+_mac_policy_list$',symbols,re.M)
    if not match:raise SystemExit('Cannot locate actual MAC policy list')
    plan=output/'mac-policy-layout.json';plan.write_text(json.dumps(dict(address=int(match[1],16),layout=layout,object_sha256=dwarf),indent=2)+'\n')
    gdb_command+=['--mac-policy-layout',plan]
if args.entry_min_pid and (not args.entry_process_name or not 1<=args.entry_min_pid<1<<31):parser.error('Minimum PID requires a named process and a positive bounded PID')
if args.entry_process_name:gdb_command+=['--entry-process-name',args.entry_process_name,'--entry-min-pid',str(args.entry_min_pid)]
if args.capture_qemu_screen:gdb_command+=['--capture-screen']
if args.qemu_ramfb:
    gdb_command += ['--qemu-ramfb']
if args.virtio_console_socket:
    gdb_command += ['--virtio-console-socket', args.virtio_console_socket]
if args.follow_target_main:
    gdb_command += ['--follow-entrypoint-arg', '1', '--follow-main-entry-offset', str(main_input['entry_offset']),
                    '--read-memory', 'fffff4025:1', '--read-memory', 'fffff4037:1']
if display_plan:
    if json.loads(display_plan.read_text())['native_sha256'] != prelink_report['native_sha256']:
        raise SystemExit('Display observer layout/symbols must belong to this exact source kernel')
    gdb_command += ['--main-cache-query-plan', display_plan]
if process_plan:
    if json.loads(process_plan.read_text())['native_sha256'] != prelink_report['native_sha256']:
        raise SystemExit('Process observer layout must belong to this exact source kernel')
    gdb_command += ['--process-layout-plan', process_plan]
if args.inspect_ui_threads:
    gdb_command.append('--inspect-ui-threads')
iogpu_component = None
if args.load_iogpu and 'com.apple.iokit.IOGPUFamily' in prelink_report['components']:
    sys.path.insert(0, str(ROOT / 'kits/XnuPrelink'))
    from native_prelink import macho, backed_offset
    target = prelink_report['module_entrypoints']['com.apple.iokit.IOGPUFamily']['start_va']
    candidate = args.kernel.read_bytes()
    at = backed_offset(macho(candidate)['segments'], target, 16, len(candidate))
    iogpu_component = dict(start=hex(target), original_start=hex(target - prelink_report['slide']),
                           entry_prefix=candidate[at:at + 16].hex())
    gdb_command += ['--trace-address', hex(target), '--read-memory', f'{target:x}:10']
mobile_component = None
if args.load_mobile_graphics and 'com.apple.iokit.IOMobileGraphicsFamily' in prelink_report['components']:
    sys.path.insert(0, str(ROOT / 'kits/XnuPrelink'))
    from native_prelink import macho, backed_offset
    target = prelink_report['module_entrypoints']['com.apple.iokit.IOMobileGraphicsFamily']['start_va']
    candidate = args.kernel.read_bytes()
    at = backed_offset(macho(candidate)['segments'], target, 16, len(candidate))
    mobile_component = dict(start=hex(target), original_start=hex(target - prelink_report['slide']),
                            entry_prefix=candidate[at:at + 16].hex(), entry_trace_requested=not (args.trace_mobile_graphics_factories or args.follow_display_mode or args.follow_metal_device))
    if not (args.trace_mobile_graphics_factories or args.follow_display_mode or args.follow_metal_device):
        gdb_command += ['--trace-address', hex(target)]
    gdb_command += ['--read-memory', f'{target:x}:10']
if args.inspect_compression:
    match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+_decompressors$', symbols, re.M)
    if not match or not prelink_report:
        raise SystemExit('Compression inspection requires actual native registration storage and its exact original-component candidate')
    for kind in (3, 4):
        request = f'{int(match[1], 16) + kind * 8:x}:0:30'
        compression_requests[str(kind)] = request
        gdb_command += ['--read-indirect', request]
if args.armvirt:
    gdb_command.extend(['--gic-version', '3'])
if args.smp > 1:
    gdb_command.extend(['--smp', str(args.smp)])
if block_image:
    gdb_command += ['--virtio-udif-image' if args.virtio_udif_image else '--virtio-block-image', block_image]
    if args.missing_virtio_device:
        gdb_command += ['--missing-virtio-device']
if args.virtio_extra_block_image:
    gdb_command += ['--virtio-extra-block-image', args.virtio_extra_block_image]
if args.entry_after:
    match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + re.escape(args.entry_after) + '$', symbols, re.M)
    if not match:
        raise SystemExit('Cannot resolve actual primary observation activation entry')
    gdb_command += ['--primary-start-address', '0x' + match[1]]
if args.log_kernel_strings_after:
    for name, option in ((args.log_kernel_strings_after, '--cstring-start-address'), ('_printf', '--cstring-log-address')):
        match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + re.escape(name) + '$', symbols, re.M)
        if not match:
            raise SystemExit(f'Cannot resolve actual delayed log function {name}')
        gdb_command += [option, '0x' + match[1]]
if args.log_registry_strings:
    match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+__ZN15IORegistryEntry11setPropertyEPKcS1_$', symbols, re.M)
    if not match:
        raise SystemExit('Cannot resolve actual registry string-property setter')
    gdb_command += ['--registry-string-log-address', '0x' + match[1]]
if args.follow_cache_leaf:
    gdb_command += ['--also-stop', hex(user_addresses['_checkpoint'])]
    gdb_command += ['--follow-entrypoint-arg', '0', '--follow-entrypoint-checkpoint-offset',
                    str(leaf_record['cache_leaf_input']['success_return_offset']), '--finish-followed-checkpoint']
for number in args.log_syscall_number:
    gdb_command += ['--syscall-number', str(number)]
if args.log_syscalls_after:
    match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + re.escape(args.log_syscalls_after) + '$', symbols, re.M)
    if not match:
        raise SystemExit('Cannot resolve actual syscall-log activation entry')
    gdb_command += ['--syscall-start-address', '0x' + match[1]]
if args.log_syscalls or args.log_syscalls_after:
    for name in ('_unix_syscall', '_mach_syscall'):
        match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + name + '$', symbols, re.M)
        if not match:
            raise SystemExit('Cannot resolve the actual syscall handler')
        gdb_command += ['--syscall-log-address', '0x' + match[1]]
if args.inspect_entry_translations:
    gdb_command += ['--inspect-entry-translations']
for request in args.read_frame_indirect:
    gdb_command += ['--read-frame-indirect', request]
if args.read_frame_locals:
    gdb_command.append('--read-frame-locals')
for request in args.read_saved_user_register:gdb_command+=['--read-saved-user-register',request]
if args.inspect_entry_user_state:
    gdb_command.append('--inspect-entry-user-state')
if args.finish_function:
    gdb_command.append('--finish-function')
    if args.verified_root_probe:
        gdb_command += ['--read-entry-indirect', '0:0:40', '--read-entry-indirect', '1:0:20']
for option, value in (('--entry-kernel-bytes-field', args.entry_kernel_bytes_field),
                      ('--entry-register-equals', args.entry_register_equals)):
    if value:
        gdb_command += [option, value]
gdb_command += ['--entry-max-skips', str(args.entry_max_skips)]
for request in args.read_entry_region:
    gdb_command += ['--read-entry-region', request]
if args.entry_user_string_field:
    gdb_command += ['--entry-user-string-field', args.entry_user_string_field]
for request in args.read_entry_indirect:
    gdb_command += ['--read-entry-indirect', request]
for request in args.read_entry_user_vector:
    gdb_command += ['--read-entry-user-vector', request]
for request in args.read_entry_user_indirect:
    gdb_command += ['--read-entry-user-indirect', request]
    if args.load_apfs and args.break_symbol == '_vfs_fsadd':
        gdb_command += ['--read-entry-indirect', '0:0:90', '--read-entry-indirect', '1:0:80']
fallback_symbols = {}
for fallback_name in ('_panic', '_panic_with_options'):
    if args.break_symbol == fallback_name:
        continue
    fallback = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + fallback_name + '$', symbols, re.M)
    if fallback:
        gdb_command.extend(['--also-stop', f'0x{fallback[1]}'])
        fallback_symbols[int(fallback[1], 16)] = fallback_name
if args.kext_logs:
    match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+_OSKextLog$', symbols, re.M)
    if not match:
        raise SystemExit('Cannot resolve OSKextLog')
    gdb_command.extend(['--kext-log-address', f'0x{match[1]}'])
trace_symbols = {}
if iogpu_component:
    trace_symbols[int(iogpu_component['start'], 16)] = 'com.apple.iokit.IOGPUFamily:kmod_start'
if mobile_component:
    if not (args.follow_display_mode or args.follow_metal_device):trace_symbols[int(mobile_component['start'],16)]='com.apple.iokit.IOMobileGraphicsFamily:kmod_start'
    if args.mobile_graphics_client_probe and not (args.follow_display_mode or args.follow_metal_device):
        entries = ((0xfffffff00677b420, 'IOMobileFramebuffer::MetaClass::alloc'),
                   (0xfffffff00677b620, 'IOMobileFramebufferService::MetaClass::alloc'),
                   (0xfffffff0067866d4, 'IOMobileFramebufferLegacy::MetaClass::alloc')) if args.trace_mobile_graphics_factories else (
                   (0xfffffff006778d40, 'IOMobileFramebufferUserClient::externalMethod'),)
        for original, name in entries:
            address = original + prelink_report['slide']
            trace_symbols[address] = name
            gdb_command += ['--trace-address', hex(address)]
for name in args.trace_symbol:
    match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + re.escape(name) + '$', symbols, re.M)
    if not match:
        raise SystemExit(f'Cannot resolve trace symbol {name}')
    trace_symbols[int(match[1], 16)] = name
    gdb_command.extend(['--trace-address', f'0x{match[1]}'])
if prelink_report and not args.skip_initializer_traces:
    for identifier in ('com.apple.kec.corecrypto', 'com.apple.driver.AppleMobileFileIntegrity',
                       'com.apple.AppleFSCompression.AppleFSCompressionTypeZlib'):
        if identifier not in prelink_report['module_entrypoints']:
            continue
        address = prelink_report['module_entrypoints'][identifier]['start_va']
        trace_symbols[address] = identifier + ':kmod_start'
        gdb_command.extend(['--trace-address', hex(address)])
    if args.load_apfs and 'com.apple.filesystems.apfs' in prelink_report['module_entrypoints']:
        address = prelink_report['module_entrypoints']['com.apple.filesystems.apfs']['start_va']
        trace_symbols[address] = 'com.apple.filesystems.apfs:kmod_start'
        gdb_command.extend(['--trace-address', hex(address)])
    for identifier, address in prelink_report.get('early_security_initializers', {}).items():
        trace_symbols[address] = identifier + ':early_security_init'
        gdb_command.extend(['--trace-address', hex(address)])
    for name in ('_register_crypto_functions', '_register_and_init_prng', '_amfi_interface_register', '_mac_policy_register'):
        match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + name + '$', symbols, re.M)
        if match:
            trace_symbols[int(match[1], 16)] = name
            gdb_command.extend(['--trace-address', f'0x{match[1]}'])
inspections = [('_PAGE_SHIFT_CONST', 4), ('_page_shift', 4), ('_page_shift_user32', 4), ('_page_size', 8)]
if args.qemu_accel == 'hvf':
    inspections += [('_initproc', 8), ('_gPanicBase', 8), ('_gPanicSize', 4), ('_panic_info', 8),
                    ('_gPhysBase', 8), ('_gPhysSize', 8), ('_mem_size', 8), ('_mem_actual', 8),
                    ('_cs_validate_page_bad_hash', 8), ('_cs_validate_page_no_hash', 8)]
owner_cache_globals = ('_native_owner_cache_stage', '_native_owner_cache_status', '_native_owner_cache_mount_status',
    '_native_owner_cache_readonly', '_native_owner_cache_authorized', '_native_owner_cache_root_recheck',
    '_native_owner_cache_selected_device', '_native_owner_cache_mounted_device')
has_owner_cache = re.search(r'\s_native_owner_cache_stage$', symbols, re.M) is not None
if has_owner_cache:
    inspections += [(name, 4) for name in owner_cache_globals] + [('_native_owner_cache_device_path', 64)]
carrier_globals = (('_native_owner_cache_carrier_accepts', 8), ('_native_owner_cache_carrier_rejects', 8),
                   ('_native_owner_cache_carrier_root_device', 4), ('_native_owner_cache_carrier_file_device', 4))
has_owner_carrier = re.search(r'\s_native_owner_cache_carrier_accepts$', symbols, re.M) is not None
if has_owner_carrier:
    inspections += list(carrier_globals)
has_owner_manifest = re.search(r'\s_native_owner_boot_manifest_status$', symbols, re.M) is not None
if args.conflicting_boot_manifest and not has_owner_manifest:
    parser.error('Conflict refusal requires the enabled owner metadata publisher')
if has_owner_manifest:
    inspections += [('_native_owner_boot_manifest_status', 4), ('_native_owner_boot_manifest_hash', 48)]
has_owner_data = re.search(r'\s_native_owner_data_status$', symbols, re.M) is not None
if has_owner_data:
    inspections += [(name, 4) for name in ('_native_owner_data_status', '_native_owner_data_stage',
                    '_native_owner_data_readonly', '_native_owner_data_device')]
    inspections += [('_native_owner_data_seed_base', 8), ('_native_owner_data_seed_size', 8), ('_native_owner_data_seed_sha256', 32)]
has_owner_data_path = re.search(r'\s_native_owner_data_device_path$', symbols, re.M) is not None
if has_owner_data_path:
    inspections += [('_native_owner_data_device_path', 64)]
composition_globals = (('_native_owner_cache_actual_mount_flags', 8), ('_native_owner_cache_original_root', 8),
                       ('_native_owner_cache_current_root', 8), ('_native_owner_cache_native_union', 4), ('_rootvnode', 8))
has_composition = re.search(r'\s_native_owner_cache_native_union$', symbols, re.M) is not None
if has_composition:
    inspections += list(composition_globals)
ram_block_globals = (('_native_ram_block_ready', 4), ('_native_ram_block_bytes', 8),
                     ('_native_ram_block_reads', 8), ('_native_ram_block_writes', 8), ('_native_ram_block_failures', 8))
has_ram_block = re.search(r'\s_native_ram_block_ready$', symbols, re.M) is not None
console_globals = tuple(('_native_console_' + name, size) for name, size in (
    ('ready', 4), ('tx_requests', 4), ('rx_requests', 4), ('failures', 4),
    ('tx_bytes', 8), ('rx_bytes', 8), ('mmio', 8)))
has_console = re.search(r'\s_native_console_ready$', symbols, re.M) is not None
if has_console:
    inspections += list(console_globals)
gpu_broker_globals=tuple(('_native_gpu_broker_'+name,size) for name,size in (
    ('stage',4),('status',4),('clients',4),('active',4),('closed',4),('requests',4),('failures',4),('refusals',4),('reply_bytes',8)))
has_gpu_broker=re.search(r'\s_native_gpu_broker_stage$',symbols,re.M) is not None
if has_gpu_broker:inspections+=list(gpu_broker_globals)
has_gpu_cpu_contexts=re.search(r'\s_native_gpu_broker_cpu_context_count$',symbols,re.M) is not None
if has_gpu_cpu_contexts:inspections+=[('_native_gpu_broker_cpu_context_count',4),('_native_gpu_broker_cpu_contexts',512)]
gpu_shared_globals=tuple('_native_gpu_shared_'+name for name in ('exports','imports','drops','refusals','tokens_live','ports'))
has_gpu_shared_contexts=all(re.search(r'\s'+name+'$',symbols,re.M) for name in gpu_shared_globals)
if has_gpu_shared_contexts:inspections.extend((name,4) for name in gpu_shared_globals)
accelerator_globals=tuple(('_native_accelerator_'+name,size) for name,size in (
    ('stage',4),('status',4),('allocated',4),('initialized',4),('parent_match',4),('unrelated_match',4),('attached',4),('released',4),('size',4),
    ('instances_before',4),('instances_live',4),('instances_after',4),('object',8),('vptr',8),('parent',8),('superclass',8)))
has_accelerator=re.search(r'\s_native_accelerator_stage$',symbols,re.M) is not None
if args.accelerator_abi_probe and not has_accelerator:parser.error('Explicit accelerator ABI component is absent from this kernel')
if has_accelerator:inspections+=list(accelerator_globals)
original_client_globals=tuple(('_native_original_client_'+name,size) for name,size in (
    ('stage',4),('status',4),('allocated',4),('initialized',4),('parent_match',4),('unrelated_match',4),('attached',4),('released',4),('size',4),('parent_size',4),
    ('instances_before',4),('instances_live',4),('instances_after',4),('wrong_start',4),('provider_initialized',4),('object',8),('vptr',8),('meta',8),('parent',8)))
has_original_client=re.search(r'\s_native_original_client_stage$',symbols,re.M) is not None
if args.original_client_abi_probe and not has_original_client:parser.error('Explicit original-client ABI instrument is absent from this kernel')
if has_original_client:inspections+=list(original_client_globals)
original_provider_globals=tuple(('_native_original_provider_'+name,size) for name,size in (
    ('stage',4),('status',4),('allocated',4),('initialized',4),('parent_match',4),('attached',4),('registered',4),('released',4),('size',4),
    ('instances_before',4),('instances_live',4),('instances_after',4),('callback',4),('start_returned',4),('start_result',4),('object',8),('vptr',8),('parent',8),('backend',8)))
# Optional new factory counters keep older exact kernels observable.
original_provider_globals+=tuple(('_native_original_provider_'+name,size) for name,size in (
    ('factory_returned',4),('factory_result',4),('client_type',4),('client_instances_before',4),('client_instances_live',4),('client_instances_at_callback',4),('descriptor_refused',4),('descriptor_provisioned',4),('factory_out_client',8))
    if re.search(r'\s_native_original_provider_'+name+'$',symbols,re.M))
has_original_provider=re.search(r'\s_native_original_provider_stage$',symbols,re.M) is not None
if args.original_provider_probe and not has_original_provider:parser.error('Original provider instrument absent from kernel')
if has_original_provider:inspections+=list(original_provider_globals)+[('_native_original_provider_frame',128)]
provider_client_capture=None
if args.original_provider_probe=='client-factory' and args.original_provider_client_type&0xffff==1:
    frame=re.search(r'^([0-9a-fA-F]+)\s+\S\s+_native_original_provider_frame$',symbols,re.M)
    if not frame:parser.error('Actual original provider frame absent')
    # Read-only: captured x1 is the original client's +280 output field. The
    # independently audited original call site determines the containing object.
    provider_client_capture=f'{int(frame[1],16)+8:x}:-118:130'
    gdb_command+=['--read-indirect',provider_client_capture]

gop_globals=tuple(('_native_gop_'+name,size) for name,size in (
    ('ready',4),('failures',4),('transfers',8),('bytes',8),('physical',8),('virtual',8)))
has_gop=re.search(r'\s_native_gop_ready$',symbols,re.M) is not None
if has_gop:inspections+=list(gop_globals)
legacy_globals = tuple(('_native_legacy_'+name,size) for name,size in (
    ('stage',4),('meta_status',4),('init_result',4),('start_result',4),('probe_match',4),('parent_match',4),
    ('object_size',4),('released',4),('object',8),('nub',8),('workloop',8),('guard_slot',4),('guard_object',8),('guard_caller',8),
    ('surface_status',4),('surface_found',4),('video_base',8),('video_bytes',8)))
has_legacy = re.search(r'\s_native_legacy_stage$',symbols,re.M) is not None
if re.search(r'\s_native_legacy_gop_map$',symbols,re.M):
    legacy_globals+=tuple(('_native_legacy_gop_'+name,size) for name,size in (
        ('map',8),('virtual',8),('physical',8),('bytes',8),('width',4),('height',4)))
if re.search(r'\s_native_legacy_transfer_calls$',symbols,re.M):
    legacy_globals+=tuple(('_native_legacy_'+name,size) for name,size in (('transfer_calls',4),('transfer_status',4),('transfer_bytes',8),('transfer_request',8)))
if re.search(r'\s_native_legacy_retirement_calls$',symbols,re.M):
    legacy_globals+=tuple(('_native_legacy_'+name,size) for name,size in (('retirement_calls',4),('retired_generation',4),('presented_generation',4),('retired_frames',4),('retired_current',8),('retired_pending',8)))
if re.search(r'\s_native_legacy_swap_validation_calls$',symbols,re.M):
    legacy_globals+=tuple(('_native_legacy_'+name,size) for name,size in (('swap_validation_calls',4),('swap_validation_result',4),('swap_validation_reason',4),('swap_request',8),('swap_surface',8)))
if re.search(r'\s_native_legacy_pm_status$',symbols,re.M):
    legacy_globals+=tuple(('_native_legacy_'+name,4) for name in ('pm_stage','pm_status','pm_calls','pm_callbacks','pm_ordinal'))
if re.search(r'\s_native_legacy_unit_scale_status$',symbols,re.M):
    legacy_globals+=tuple(('_native_legacy_'+name,4) for name in ('unit_scale_status','unit_scale_calls','chosen_scale','chosen_rotation'))
has_legacy_client=re.search(r'\s_native_legacy_client_calls$',symbols,re.M) is not None
if has_legacy_client:
    legacy_globals+=tuple(('_native_legacy_'+name,size) for name,size in (
        ('registration_calls',4),('properties_length',4),('client_calls',4),('client_type',4),('client_pid',4),('client_status',4),('client_task',8),('client_object',8)))
    if re.search(r'\s_native_legacy_dt_attached$',symbols,re.M):legacy_globals+=(('_native_legacy_dt_attached',4),)
    inspections+=[('_native_legacy_properties',4096),('_native_legacy_client_class',64)]
if has_legacy:inspections += list(legacy_globals)
ufs_globals = tuple(('_native_ufs_'+name,size) for name,size in (
    ('probe_calls',4),('matched',4),('probe_requested',4),('mapped',4),('status',4),
    ('cap',4),('version',4),('hcs',4),('hce',4),('utrl_ready',4),('uic_status',4),('uic_result',4)))
has_ufs = re.search(r'\s_native_ufs_matched$',symbols,re.M) is not None
if has_ufs: inspections += list(ufs_globals)
if args.data_ramdisk and not (has_owner_data or has_ram_block):
    parser.error('Scratch Data requires its explicitly enabled kernel mount or storage instrument')
if has_ram_block:
    inspections += list(ram_block_globals) + [('_native_ram_block_seed_sha256', 32)]
if args.inspect_dyld_flags:
    inspections += [('_dyld_flags', 8), ('_commpage_rw_addr', 8)]
    if re.search(r'\s_native_owner_cache_dyld_flags$', symbols, re.M):
        inspections += [('_native_owner_cache_dyld_flags', 8)]
if args.owner_root_audit or args.owner_root_accepted or args.inspect_owner_root:
    inspections += [('_native_owner_root_apple_autherr', 4), ('_native_owner_root_decision', 4), ('_native_owner_root_readonly', 4), ('_native_owner_root_mount_device', 4), ('_native_owner_root_selected_device', 4),
                    ('_native_verified_block_root_device', 4), ('_native_verified_block_root_media_matches', 4),
                    ('_native_verified_block_root_provider_depth', 4), ('_native_verified_block_root_uuid_match', 4),
                    ('_native_verified_block_wrong_uuid_refused', 4), ('_native_verified_block_root_uuid', 37),
                    ('_native_owner_root_trust_enabled', 4), ('_native_owner_root_accepted', 4), ('_amfi', 8)]
if args.verified_root_probe:
    inspections += [('_native_verified_root_status', 4), ('_native_verified_root_results', 32),
                    ('_native_verified_root_signature_calls', 4), ('_native_verified_root_block_count', 8),
                    ('_native_verified_root_manifest_pointer', 8), ('_amfi', 8)]
has_provider = re.search(r'\s_source_corecrypto14_status$', symbols, re.M) is not None
extra_integrity_globals = [name for name in ('_native_virtio_verified_devices', '_native_virtio_ambiguous_policies')
                           if re.search(r'\s' + name + '$', symbols, re.M)]
inspections += [(name, 4) for name in extra_integrity_globals]
if args.require_crypto14 and not has_provider:
    raise SystemExit('This kernel has no source corecrypto 14 provider')
if has_provider:
    inspections += [('_source_corecrypto14_status', 4), ('_g_crypto_funcs', 8), ('_prng_ready', 4)]
if prelink_report:
    inspections += [('_g_crypto_funcs', 8), ('_crypto_init', 1), ('_prng_ready', 4)]
    if prelink_report.get('early_security_initializers'):
        inspections += [('_mac_late', 4)]
has_pthread = re.search(r'\s_source_pthread_status$', symbols, re.M) is not None
if has_pthread:
    inspections += [('_source_pthread_status', 4), ('_pthread_functions', 8), ('_pthread519_pthread_kern', 8)]
aes_globals = ('_native_aes_kat_status', '_native_aes_interface_status', '_native_aes_registered',
               '_native_aes_completed', '_native_aes_unsupported_key')
has_native_aes = re.search(r'\s_native_aes_kat_status$', symbols, re.M) is not None
if has_native_aes:
    aes_globals = tuple(name for name in aes_globals if re.search(r'\s' + name + '$', symbols, re.M))
    inspections += [(name, 4) for name in aes_globals]
if args.load_apfs:
    inspections += [('_native_apfs_load_status', 4), ('_native_apfs_registered', 4), ('_native_apfs_vfsops', 8)]
has_hid_probe = re.search(r'\s_native_hid_stage$', symbols, re.M) is not None
if args.load_hid_input and not has_hid_probe:
    parser.error('Build the original HID initialization observation first')
if has_hid_probe:
    inspections += [('_native_hid_stage',4),('_native_hid_resource_found',4),('_native_hid_load_status',4),('_native_hid_matching_load_status',4),('_native_hid_class_sizes',20)]
    inspections += [('_native_hid_input_meta_status',4),('_native_hid_input_object',8),('_native_hid_input_events',32),('_native_hid_input_results',32)]
has_iogpu_probe = re.search(r'\s_native_iogpu_load_status$', symbols, re.M) is not None
if args.load_iogpu and not has_iogpu_probe:
    parser.error('Build the explicit original IOGPUFamily load diagnostic first')
if has_iogpu_probe:
    inspections += [('_native_iogpu_load_status', 4)]
has_mobile_graphics_probe = re.search(r'\s_native_mobile_graphics_load_status$', symbols, re.M) is not None
constant_fields = ('status', 'refusal_mask', 'output_preserved', 'written_bytes', 'padded_bytes', 'allocations_released')
constant_pointers = ('a_pointer', 'b_pointer', 'output_pointer')
has_constant_probe = re.search(r'\s_native_constants_status$', symbols, re.M) is not None
if (args.constant_uploads_probe or args.inspect_constant_uploads) and not has_constant_probe:
    parser.error('Build the explicit native constant upload diagnostic archive first')
if has_constant_probe:
    inspections += [('_native_constants_' + name, 4) for name in constant_fields]
    inspections += [('_native_constants_' + name, 8) for name in constant_pointers]
    inspections += [('_native_constants_physical', 48)]
smmu4k_fields = ('status', 'table_pages', 'leaf_pages', 'refusal_mask', 'output_preserved', 'allocations_released')
has_smmu4k_probe = re.search(r'\s_native_smmu4k_status$', symbols, re.M) is not None
if (args.smmu4k_probe or args.inspect_smmu4k) and not has_smmu4k_probe:
    parser.error('Build the explicit native SMMU4K diagnostic archive first')
if has_smmu4k_probe:
    inspections += [('_native_smmu4k_' + name, 4) for name in smmu4k_fields]
    inspections += [('_native_smmu4k_' + name, 8) for name in ('pool_pointer', 'data_pointer', 'cpu_mair')]
    inspections += [('_native_smmu4k_pool_physical', 48), ('_native_smmu4k_data_physical', 16)]
pm4_fields = ('status', 'packets', 'refusal_mask', 'output_preserved', 'bit_refusals', 'input_preserved')
has_pm4_probe = re.search(r'\s_native_adreno_pm4_status$', symbols, re.M) is not None
if args.adreno_pm4_probe and not has_pm4_probe:
    parser.error('Build the explicit native Adreno PM4 diagnostic archive first')
if has_pm4_probe:
    inspections += [('_native_adreno_pm4_' + name, 4) for name in pm4_fields]
has_adreno_probe = re.search(r'\s_native_adreno_firmware_status$', symbols, re.M) is not None
if (args.adreno_firmware_probe or args.inspect_adreno_firmware) and not has_adreno_probe:
    parser.error('Build the explicit native Adreno firmware diagnostic archive first')
adreno_fields = ('status', 'records', 'payload_bytes', 'refusal_mask', 'output_preserved')
if has_adreno_probe:
    inspections += [('_native_adreno_firmware_' + name, 4) for name in adreno_fields]
    inspections += [('_native_adreno_firmware_sha256', 32), ('_native_adreno_firmware_pointer', 8),
                    ('_native_adreno_firmware_image_size', 8)]
if has_mobile_graphics_probe:
    inspections += [('_native_mobile_graphics_load_status', 4)]
has_mobile_client_probe = re.search(r'\s_native_mobile_graphics_client_results$', symbols, re.M) is not None
if re.search(r'\s_native_mobile_provider_stage$', symbols, re.M):
    inspections += [(name, size) for name, size in (
        ('_native_mobile_provider_stage', 4), ('_native_mobile_provider_meta_status', 4),
        ('_native_mobile_provider_query_status', 4), ('_native_mobile_provider_object', 8),
        ('_native_mobile_provider_client', 8), ('_native_mobile_provider_dimensions', 16),
        ('_native_mobile_provider_expected', 16), ('_native_mobile_provider_parent_match', 4),
        ('_native_mobile_provider_released', 4))]
mobile_client_fields = ('abstract_null_mask', 'client_object', 'client_vptr', 'client_meta',
                        'client_size', 'client_init', 'client_released')
if has_mobile_client_probe:
    inspections += [('_native_mobile_graphics_' + name, 8 if name in ('client_object', 'client_vptr', 'client_meta') else 4)
                    for name in mobile_client_fields]
    inspections += [('_native_mobile_graphics_client_results', 12)]
if block_image and re.search(r'\s_native_virtio_manifest_ready$', symbols, re.M):
    inspections += [('_native_virtio_manifest_ready', 4), ('_native_virtio_verified_blocks', 8),
                    ('_native_virtio_integrity_failures', 4), ('_native_virtio_verified_manifest_pointer', 8),
                    ('_native_virtio_verified_key_pointer', 8)]
if block_image:
    inspections += [('_native_virtio_ready', 4), ('_native_virtio_read_requests', 4), ('_native_virtio_read_failures', 4),
                    ('_native_virtio_sectors', 8), ('_native_virtio_mmio_physical', 8), ('_native_virtio_first_sector_sha256', 32)]
if args.native_user:
    inspections += [('_amfi', 8), ('_cs_validate_page_bad_hash', 8), ('_cs_validate_page_no_hash', 8)]
native_hash_cache = re.search(r'\s_cs_native4k_hash_cache_version$', symbols, re.M) is not None
if args.mutate_own_vnode_page is not None or cache_fault or main_fault:
    if not native_hash_cache:
        raise SystemExit('Mapped-page fault injection requires the native integrity-cache kernel')
    entry = re.search(r'^([0-9a-fA-F]+)\s+\S\s+_cs_validate_hash$', symbols, re.M)
    if not entry:
        raise SystemExit('Cannot resolve actual page-integrity validation')
    image_bytes = main_bytes if main_fault else (args.cache_page_source if cache_fault else payloads / 'launchd.macho').read_bytes()
    expected_cache_sha = (leaf_record['cache_leaf_input']['file_sha256'] if args.follow_cache_leaf else
                          '3d923c404fe519184a99042b60a4cb3d37247dcb8b070242ed3e670d4d523d04')
    if cache_fault and hashlib.sha256(image_bytes).hexdigest() != expected_cache_sha:
        raise SystemExit('Expected the exact unchanged supplied cache input identified by this probe')
    offset = main_input['entry_offset'] if main_fault else args.mutate_cache_vnode_page if cache_fault else args.mutate_own_vnode_page
    page = offset & ~4095
    if offset < 0 or page + 4096 > len(image_bytes):
        raise SystemExit('Select a byte in a complete own fixture page')
    address = int(entry[1], 16)
    trace_symbols[address] = '_cs_validate_hash'
    gdb_command.extend(['--trace-address', hex(address), '--mutate-mapped-vnode-page',
        f'{address:x}:{page:x}:{offset & 4095:x}:{hashlib.sha256(image_bytes[page:page + 4096]).hexdigest()}'])
    if cache_fault or main_fault:
        dwarf = subprocess.check_output(['xcrun', 'dwarfdump', '--name=cs_blob', '--show-children',
            ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/bsd/DEVELOPMENT/ubc_subr.o'], text=True)
        field = re.search(r'DW_AT_name\s+\("csb_cdhash"\)[\s\S]*?DW_AT_data_member_location\s+\((0x[0-9a-f]+)\)', dwarf)
        if main_fault:
            original_record = json.loads((ROOT / 'build/target-dyld-fixture/inputs.json').read_text())
            if original_record['files'][0]['sha256'] != hashlib.sha256(image_bytes).hexdigest():
                raise SystemExit('Require the exact unchanged supplied launchd signing identity')
            probe_metadata = dict(original_file_sha256=original_record['files'][0]['sha256'], original_cdhash=original_record['original_cdhashes'][0])
            gdb_command += ['--mapped-vnode-max-hits', '4096']
        else:
            probe_metadata = (dict(original_file_sha256=leaf_record['cache_leaf_input']['file_sha256'],
                                   original_cdhash=leaf_record['cache_leaf_input']['original_cdhash']) if args.follow_cache_leaf else
                              json.loads((args.native_user_image.parent / 'file-probe.json').read_text()))
        if not field or probe_metadata['original_file_sha256'] != hashlib.sha256(image_bytes).hexdigest():
            raise SystemExit('Require actual compiled cs_blob layout and exact original cache probe identity')
        gdb_command += ['--mapped-vnode-cdhash', f'{int(field[1], 16):x}:' + probe_metadata['original_cdhash']]
if args.mutate_own_ramdisk_after_auth is not None:
    if not native_hash_cache:
        raise SystemExit('Post-authentication mutation requires the native integrity-cache kernel')
    entry = re.search(r'^([0-9a-fA-F]+)\s+\S\s+_cs_native4k_prepare$', symbols, re.M)
    md0 = re.search(r'^([0-9a-fA-F]+)\s+\S\s+_mdev$', symbols, re.M)
    if not entry or not md0:
        raise SystemExit('Cannot resolve actual authentication/md0 state symbols')
    image_bytes = (payloads / 'launchd.macho').read_bytes()
    address = int(entry[1], 16)
    trace_symbols[address] = '_cs_native4k_prepare'
    gdb_command.extend(['--trace-address', hex(address), '--mutate-md0-after-return',
        f'{address:x}:{md0[1]}:{len(image_bytes):x}:{hashlib.sha256(image_bytes).hexdigest()}:{args.mutate_own_ramdisk_after_auth:x}'])
if native_hash_cache:
    inspections += [('_cs_native4k_hash_cache_version', 4), ('_cs_native4k_full_blocks', 8),
                    ('_cs_native4k_page_checks', 8), ('_cs_native4k_ready_blobs', 8)]
if args.armvirt and re.search(r'\s_armvirt_platform_configured$', symbols, re.M):
    inspections += [('_armvirt_platform_configured', 4), ('_armvirt_platform_child_count', 4),
                    ('_armvirt_platform_cpu_count', 4), ('_armvirt_platform_bus_count', 4)]
    if re.search(r'\s_armvirt_platform_defaults_count$', symbols, re.M):
        inspections += [('_armvirt_platform_defaults_count', 4)]
if re.search(r'\s_armdt_platform_configured$', symbols, re.M):
    inspections += [('_armdt_platform_configured', 4), ('_armdt_platform_child_count', 4),
                    ('_armdt_platform_cpu_count', 4), ('_armdt_platform_bus_count', 4),
                    ('_armdt_platform_defaults_count', 4), ('_armdt_platform_nvram_proxy', 4)]
    if re.search(r'\s_armdt_platform_device_count$', symbols, re.M):
        inspections += [('_armdt_platform_device_count', 4)]
if args.armcpu:
    inspections += [('_armcpu_registered', 4), ('_armcpu_gic_ready', 4), ('_armcpu_timer_interrupts', 8),
                    ('_armcpu_ipi_interrupts', 8), ('_gCPUsRunning', 1)]
    if args.smp > 1:
        inspections += [('_armcpu_smp_running', 4), ('_armcpu_smp_step', 32), ('_armcpu_smp_psci_rc', 32), ('_armcpu_smp_conduit', 4)]
inspections = list(dict.fromkeys(inspections))
pgz_probe_globals = [('case', 4), ('stage', 4), ('zone', 4), ('expected_zone', 4), ('metadata', 4),
                     ('backing', 8), ('alias', 8), ('argument', 8)]
if args.zone_pgz_probe_case:
    inspections += [('_native_zone_pgz_probe_' + name, width) for name, width in pgz_probe_globals]
pgz_fix_counter = re.search(r'\s_native_zone_pgz_alignment_decodes$', symbols, re.M) is not None
if pgz_fix_counter:
    inspections += [('_native_zone_pgz_alignment_decodes', 8)]
video_layout = None
if args.inspect_boot_video:
    obj = ROOT / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/pexpert/DEVELOPMENT/pe_init.o'
    state_dwarf = subprocess.check_output(['xcrun', 'dwarfdump', '--name=PE_state', '--show-children', obj], text=True)
    video_dwarf = subprocess.check_output(['xcrun', 'dwarfdump', '--name=PE_Video', '--show-children', obj], text=True)
    def member_offset(text, name):
        match = re.search(r'DW_TAG_member[\s\S]*?DW_AT_name\s+\("' + re.escape(name) + r'"\)[\s\S]*?DW_AT_data_member_location\s+\((0x[0-9a-f]+)\)', text)
        if not match:
            raise SystemExit('Cannot derive actual PE video layout from compiler DWARF')
        return int(match[1], 16)
    size = re.search(r'DW_TAG_structure_type[\s\S]*?DW_AT_byte_size\s+\((0x[0-9a-f]+)\)', state_dwarf)
    if not size:
        raise SystemExit('Cannot derive actual PE state size')
    video_layout = dict(state_size=int(size[1], 16), video=member_offset(state_dwarf, 'video'),
                        boot_args=member_offset(state_dwarf, 'bootArgs'),
                        fields={n: member_offset(video_dwarf, n) for n in
                                ('v_baseAddr', 'v_rowBytes', 'v_width', 'v_height', 'v_depth', 'v_display')},
                        object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest())
    inspections += [('_PE_state', video_layout['state_size'])]
if args.inspect_sheng_pmgr:
    inspections += [('_sheng_pmgr_observation', 16 * 8)]
has_boot_progress = re.search(r'\s_boot_progress_observation$', symbols, re.M) is not None
if has_boot_progress:
    inspections += [('_boot_progress_observation', 24 * 8), ('_boot_progress_frozen', 4)]
    if re.search(r'\s_boot_progress_display_owned$', symbols, re.M):
        inspections += [('_boot_progress_display_owned', 4)]
for name, width in inspections:
    match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + re.escape(name) + '$', symbols, re.M)
    if not match:
        raise SystemExit(f'Cannot resolve {name}')
    request = f'{match[1]}:{width:x}'
    page_globals[name] = request
    gdb_command.extend(['--read-memory', request])
if video_layout:
    video_args_request = f"{int(page_globals['_PE_state'].split(':')[0], 16) + video_layout['boot_args']:x}:28:30"
    gdb_command += ['--read-indirect', video_args_request]
gop_captures=[];gop_spans=[]
if args.inspect_gop_scanout_bytes:
    size=args.inspect_gop_scanout_bytes
    if not has_gop or not video_layout or not 4096<=size<=4*1024*1024:parser.error('Scanout observation requires actual presenter/video and a bounded 4 KiB..4 MiB extent')
    pointer=page_globals['_native_legacy_gop_virtual' if args.legacy_display_transfer else '_native_gop_virtual'].split(':')[0]
    for offset in sorted({0,(size//2)&~4095,size-4096}):
        request=f'{pointer}:{offset:x}:1000';gop_captures.append(request);gdb_command+=['--read-indirect',request]
    for offset in range(0,size,1024*1024):
        request=f'{pointer}:{min(size-offset,1024*1024):x}:{offset:x}';gop_spans.append(request);gdb_command+=['--inspect-indirect-kernel-range',request]
constant_captures = {}
if args.inspect_constant_uploads:
    gdb_command += ['--allow-unmapped-kernel-pages']
    for label in ('a', 'b', 'output'):
        address = page_globals['_native_constants_' + label + '_pointer'].split(':')[0]
        span = address + ':2000'
        capture = address + ':0:1000'
        gdb_command += ['--read-indirect', capture, '--inspect-indirect-kernel-range', span]
        constant_captures[label] = dict(span=span, capture=capture)
smmu4k_captures = {}
if args.inspect_smmu4k:
    for label, pages in (('pool', 6), ('data', 2)):
        address = page_globals['_native_smmu4k_' + label + '_pointer'].split(':')[0]
        span = address + ':' + f'{pages * 4096:x}'
        captures = [address + f':{i * 4096:x}:1000' for i in range(pages)]
        for request in captures:
            gdb_command += ['--read-indirect', request]
        gdb_command += ['--inspect-indirect-kernel-range', span]
        smmu4k_captures[label] = dict(span=span, chunks=captures)
if args.inspect_adreno_firmware:
    adreno_input_request = page_globals['_native_adreno_firmware_pointer'].split(':')[0] + ':0:20'
    gdb_command += ['--read-indirect', adreno_input_request]
    match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+_native_adreno_firmware_image$', symbols, re.M)
    if not match:
        raise SystemExit('Cannot resolve the actual constant GMU input')
    adreno_input_bytes = json.loads((ROOT / 'scripts/data/adreno-inputs.json').read_text())['firmware']['files']['qcom/gmu_gen70200.bin']['bytes']
    adreno_input_range = f'{int(match[1], 16):x}:{adreno_input_bytes:x}'
    gdb_command += ['--inspect-kernel-range', adreno_input_range]
if block_image and '_native_virtio_verified_manifest_pointer' in page_globals and not args.skip_policy_pointer_reads:
    for name in ('_native_virtio_verified_manifest_pointer', '_native_virtio_verified_key_pointer'):
        gdb_command += ['--read-indirect', page_globals[name].split(':')[0] + ':0:20']
if args.inspect_dyld_flags:
    flags_request = page_globals['_commpage_rw_addr'].split(':')[0] + ':160:8'
    gdb_command += ['--read-indirect', flags_request]
user_requests = {}
if args.native_user:
    user_inspections = [('_results', 32), ('_user_page_size', 8), ('_old_length', 8)]
    if '_fp_context_results' in user_addresses:
        user_inspections += [('_fp_context_results',80),('_fp_context_actual',512),('_fp_context_expected',512)]
    if '_file_probe_results' in user_addresses:
        user_inspections += [('_file_probe_results', 80), ('_file_signature', 24)]
    if '_cache_leaf_results' in user_addresses:
        user_inspections += [('_cache_leaf_results', 72), ('_cache_leaf_target', 8)]
    if '_apfs_launchd_results' in user_addresses:
        user_inspections += [('_apfs_launchd_results', 104)]
    if '_apfs_mount_results' in user_addresses:
        user_inspections += [('_apfs_mount_results', 40)]
    for name, length in user_inspections:
        request = f'{user_addresses[name]:x}:{length:x}'
        user_requests[name] = request
        gdb_command.extend(['--read-memory', request])
commpage_requests = {}
if args.check_commpage:
    for name in ('_commpage_rw_addr', '_commpage_kernel_ro_addr'):
        match = re.search(r'^([0-9a-fA-F]+)\s+\S\s+' + name + '$', symbols, re.M)
        if not match:
            raise SystemExit(f'Cannot resolve {name}')
        request = f'{match[1]}:25:1'
        commpage_requests[name] = request
        gdb_command.extend(['--read-indirect', request])
if args.live_hid_dir:gdb_command.extend(['--live-hid-dir',str(args.live_hid_dir.resolve())])
subprocess.run(gdb_command, check=True)
report = json.loads((output / 'gdb-stop.json').read_text())
if has_hid_probe:
    report['native_hid'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_hid_'+name]]),'little',signed=name.endswith('load_status'))
        for name in ('stage','resource_found','load_status','matching_load_status')}
    report['native_hid']['class_sizes'] = list(struct.unpack('<5I',bytes.fromhex(report['memory'][page_globals['_native_hid_class_sizes']])))
    for name in ('input_meta_status','input_object'):
        report['native_hid'][name]=int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_hid_'+name]]),'little',signed=name=='input_meta_status')
    for name,fmt in (('input_events','<8I'),('input_results','<8i')):
        report['native_hid'][name]=list(struct.unpack(fmt,bytes.fromhex(report['memory'][page_globals['_native_hid_'+name]])))
if has_boot_progress:
    values = struct.unpack('<24Q', bytes.fromhex(report['memory'][page_globals['_boot_progress_observation']]))
    report['boot_progress'] = dict(zip(('enabled','bound','seconds','activity_at','irqs','monitor_ticks',
        'dropped','reason','reads','verified','failures','last_pc','last_psr','last_sp','tcr','ttbr0','ttbr1',
        'sctlr','stage_records','log_lines','width','height','stride','frame'), values))
    report['boot_progress']['frozen'] = int.from_bytes(bytes.fromhex(report['memory'][page_globals['_boot_progress_frozen']]), 'little')
    if '_boot_progress_display_owned' in page_globals:
        report['boot_progress']['display_owned'] = int.from_bytes(bytes.fromhex(report['memory'][page_globals['_boot_progress_display_owned']]), 'little')
if args.zone_pgz_probe_case:
    report['actual_zone_pgz_probe'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_zone_pgz_probe_' + name]]), 'little')
                                       for name, _ in pgz_probe_globals}
if pgz_fix_counter:
    report['actual_zone_pgz_alignment_decodes'] = int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_zone_pgz_alignment_decodes']]), 'little')
if video_layout:
    pe = bytes.fromhex(report['memory'][page_globals['_PE_state']])
    boot = bytes.fromhex(report['indirect_memory'][video_args_request]['bytes'])
    report['actual_boot_video'] = dict(qemu_ramfb_attached=args.qemu_ramfb, compiled_layout=video_layout,
        boot_args=dict(zip(('physical_base', 'display', 'row_bytes', 'width', 'height', 'depth'), struct.unpack('<6Q', boot))),
        pe_video={name: struct.unpack_from('<Q', pe, video_layout['video'] + offset)[0]
                  for name, offset in video_layout['fields'].items()},
        darwinboot_driver_sha256=hashlib.sha256((payloads / 'DarwinBoot.efi').read_bytes()).hexdigest(),
        native_mobile_framebuffer_qualified=False)
if args.root_match_volume_uuid:
    report['root_selection'] = dict(mechanism='chosen/root-matching IOMedia IOPropertyMatch UUID',
                                    volume_uuid=str(args.root_match_volume_uuid).upper(),
                                    bsd_name_override=False, root_authentication_bypassed=False)
report['offline_qemu_vmm_present_declared'] = args.qemu_vmm_present
report['offline_device_tree_sha256'] = hashlib.sha256((payloads / 'kernel.macho.adt').read_bytes()).hexdigest()
if args.trust_cache:
    report['trust_cache_bundle_sha256'] = hashlib.sha256(trust_sidecar.read_bytes()).hexdigest()
if cache_fault:
    report['cache_page_fault_input'] = dict(file=args.cache_page_source.name,
        sha256=hashlib.sha256(image_bytes).hexdigest(), offset=offset,
        original_file_modified=False, signatures_or_trust_modified=False,
        guest_validation_data_only=True, input_fault_instrument_only=True)
if args.native_user:
    report['native_user_image_sha256'] = hashlib.sha256((args.native_data_user_image or payloads / 'launchd.macho').read_bytes()).hexdigest()
    if args.native_user_ramdisk:
        report['offline_root_sha256'] = hashlib.sha256((payloads / 'root.img').read_bytes()).hexdigest()
registers = {name: int(value, 16) for name, value in report['system_registers'].items()}
tcr = registers['TCR_EL1']
if (tcr >> 14 & 3) != 0 or (tcr >> 30 & 3) != 2 or not registers['SCTLR_EL1'] & 1:
    raise SystemExit('FAIL: active native 4K translation was not observed')
if not registers['TTBR0_EL1'] or not registers['TTBR1_EL1']:
    raise SystemExit('FAIL: active translation bases are missing')
uart = (output / 'gdb-uart.log').read_text(errors='replace')
if 'DARWINBOOT: inputs validated; exiting boot services' not in uart or 'ASSERT' in uart:
    raise SystemExit('FAIL: the UEFI loader path was not established')
for event in report.get('trace_events', []):
    event['symbol'] = trace_symbols[int(event['pc'], 16)]
if args.qemu_accel == 'hvf':
    report['actual_panic_region'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_gPanicBase', '_gPanicSize', '_panic_info')}
if args.qemu_accel == 'hvf':
    report['actual_initproc_pointer'] = int.from_bytes(bytes.fromhex(report['memory'][page_globals['_initproc']]), 'little')
    if args.break_symbol == '_posix_spawn' and 'function_entry_arguments' in report:
        report['spawn_parent_is_initproc'] = int(report['function_entry_arguments'][0], 16) == report['actual_initproc_pointer']
    report['actual_physical_memory'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_gPhysBase', '_gPhysSize', '_mem_size', '_mem_actual')}
    report['actual_signature_failures'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_cs_validate_page_bad_hash', '_cs_validate_page_no_hash')}
report['native_4k_mmu_observed'] = True
report['ipados_userspace_boot_demonstrated'] = False
report['functional_ipados_boot_demonstrated'] = False
report['sheng_hardware_tested'] = False
if args.inspect_compression:
    report['compression_registrations'] = {kind: report['indirect_memory'][request]
                                           for kind, request in compression_requests.items()}
if args.inspect_sheng_pmgr:
    values = struct.unpack('<16Q', bytes.fromhex(report['memory'][page_globals['_sheng_pmgr_observation']]))
    report['sheng_pmgr_observation'] = dict(zip(('stage', 'status', 'parent_size', 'own_size',
        'provider', 'nub', 'bound_provider', 'read_before', 'read_after', 'own_before',
        'own_after', 'nub_before', 'nub_after', 'attached', 'registered', 'mode'), values))
report['kernel_page_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][request]), 'little')
                               for name, request in page_globals.items() if name in dict(inspections[:4])}
for name, value in report['kernel_page_globals'].items():
    if value != (4096 if name == '_page_size' else 12):
        raise SystemExit(f'FAIL: {name} reports {value}, inconsistent with native 4K policy')
text_symbols = sorted((int(address, 16), name) for address, name in
                      re.findall(r'^([0-9a-fA-F]+)\s+\S\s+(_\S+)$', symbols, re.M))
fault_pc = int(report['x1'], 16)
preceding = [(address, name) for address, name in text_symbols if address <= fault_pc]
if args.break_symbol == '_panic':
    report['panic_x1_nearest_text_symbol'] = preceding[-1][1] if preceding else None
if report.get('argument_memory', {}).get('x0', '').startswith('%s at pc'):
    arguments = struct.unpack_from('<4Q', bytes.fromhex(report['stack_bytes']))
    report['kernel_exception'] = {'pc': hex(arguments[1]), 'lr': hex(arguments[2])}
    preceding = [(address, name) for address, name in text_symbols if address <= arguments[1]]
    if preceding:
        report['kernel_exception']['nearest_symbol'] = preceding[-1][1]
        report['kernel_exception']['symbol_offset'] = hex(arguments[1] - preceding[-1][0])
    saved = report.get('stack_pointer_memory', {}).get('3', {}).get('bytes', '')
    if len(saved) >= 592 and not saved.startswith('E'):
        state = bytes.fromhex(saved)
        if struct.unpack_from('<Q', state, 264)[0] == arguments[1]:
            report['kernel_exception']['far'] = hex(struct.unpack_from('<Q', state, 280)[0])
            report['kernel_exception']['esr'] = hex(struct.unpack_from('<I', state, 288)[0])
if report.get('argument_memory', {}).get('x0') == '%s':
    raw = report.get('stack_pointer_memory', {}).get('0', {}).get('bytes', '')
    if raw and not raw.startswith('E'):
        report['panic_message'] = bytes.fromhex(raw).split(b'\0', 1)[0].decode(errors='replace')
def stack_string(index):
    raw = report.get('stack_pointer_memory', {}).get(str(index), {}).get('bytes', '')
    return bytes.fromhex(raw).split(b'\0', 1)[0].decode(errors='replace') if raw and not raw.startswith('E') else None

if report.get('argument_memory', {}).get('x0', '').startswith('unexpected SIGKILL of %s %s with reason'):
    arguments = struct.unpack_from('<5Q', bytes.fromhex(report['stack_bytes']))
    report['exec_policy_refusal'] = {'process': stack_string(0), 'namespace': arguments[2] & 0xffffffff,
                                     'code': arguments[3], 'description': stack_string(4)}
if fallback_symbols.get(int(report['pc'], 16)) == '_panic_with_options':
    report['panic_with_options'] = {'format': report.get('argument_memory', {}).get('x3'),
                                    'options': report['x2'], 'reason': report['x0']}
    if (report['panic_with_options']['format'] or '').startswith('%s -- no exit reason available'):
        arguments = struct.unpack_from('<4Q', bytes.fromhex(report['stack_bytes']))
        report['critical_process_exit'] = dict(process=stack_string(0), signal=arguments[1] & 0xffffffff,
                                               status=arguments[2] & 0xffffffff, cs_status=stack_string(3))
    if (report['panic_with_options']['format'] or '').startswith('%s %s -- exit reason namespace'):
        arguments = struct.unpack_from('<5Q', bytes.fromhex(report['stack_bytes']))
        report['fatal_user_exit'] = {'cs_status': stack_string(0), 'prefix': stack_string(1),
                                     'namespace': arguments[2] & 0xffffffff, 'code': arguments[3], 'description': stack_string(4)}
if prelink_report:
    caller = int(report['x30'], 16)
    for extent in prelink_report['extents']:
        if extent['va'] <= caller < extent['va'] + extent['size']:
            report['panic_caller_component'] = {'module': extent['module'], 'segment': extent['segment'],
                                                 'offset': hex(caller - extent['va'])}
expected_pc = report.get('function_return_target', f'0x{panic[1]}')
actual_target = int(report['pc'], 16) == int(expected_pc, 16)
if has_composition:
    report['actual_root_composition'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                                       for name, _ in composition_globals}
if has_ram_block:
    report['native_ram_block'] = dict(input=data_seed,
        state={name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little') for name, _ in ram_block_globals},
        seed_sha256=report['memory'][page_globals['_native_ram_block_seed_sha256']])
if has_owner_data:
    report['scratch_data'] = dict(input=data_seed,
        actual_device_path=bytes.fromhex(report['memory'][page_globals['_native_owner_data_device_path']]).split(b'\0', 1)[0].decode() if has_owner_data_path else None,
        state={name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little', signed=True)
               for name in ('_native_owner_data_status', '_native_owner_data_stage', '_native_owner_data_readonly', '_native_owner_data_device')},
        actual_seed_sha256=report['memory'][page_globals['_native_owner_data_seed_sha256']],
        actual_seed_bytes=int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_owner_data_seed_size']]), 'little'))
if has_owner_manifest:
    report['owner_boot_manifest'] = dict(
        status=int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_owner_boot_manifest_status']]), 'little', signed=True),
        sha384=report['memory'][page_globals['_native_owner_boot_manifest_hash']],
        domain='VerifiedRoot.OwnerBootSet.v1', firmware_personalization=False,
        conflicting_untrusted_dt_input=args.conflicting_boot_manifest)
if has_owner_cache:
    report['owner_cache_mount'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little', signed=True)
                                  for name in owner_cache_globals}
    report['owner_cache_mount']['actual_device_path'] = bytes.fromhex(report['memory'][page_globals['_native_owner_cache_device_path']]).split(b'\0')[0].decode()
if has_owner_carrier:
    report['owner_cache_carrier'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name, width in carrier_globals}
if args.inspect_dyld_flags:
    report['dyld_startup_flags'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_dyld_flags', '_native_owner_cache_dyld_flags') if name in page_globals}
    report['dyld_startup_flags']['actual_commpage_flags'] = int.from_bytes(bytes.fromhex(report['indirect_memory'][flags_request]['bytes']), 'little')
if args.owner_root_audit or args.owner_root_accepted or args.inspect_owner_root:
    report['owner_root_binding_audit'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_native_owner_root_apple_autherr', '_native_owner_root_decision', '_native_owner_root_readonly',
                     '_native_owner_root_mount_device', '_native_owner_root_selected_device',
                     '_native_verified_block_root_device', '_native_verified_block_root_media_matches',
                     '_native_verified_block_root_provider_depth', '_native_verified_block_root_uuid_match',
                     '_native_verified_block_wrong_uuid_refused', '_native_owner_root_trust_enabled', '_native_owner_root_accepted')}
    report['owner_root_binding_audit']['actual_uuid'] = bytes.fromhex(report['memory'][page_globals['_native_verified_block_root_uuid']]).split(b'\0')[0].decode()
    binding = report['owner_root_binding_audit']
    binding['boot_root_accepted'] = bool(binding['_native_owner_root_accepted'] == 1 and
        binding['_native_owner_root_trust_enabled'] == 1 and binding['_native_owner_root_decision'] == 1 and
        (args.inspect_owner_root or (args.owner_root_accepted and actual_target and report.get('function_return_stack_matched'))))
    binding['policy'] = 'independent owner signature, authenticated I/O and actual mounted-root identity'
    pointer = int.from_bytes(bytes.fromhex(report['memory'][page_globals['_amfi']]), 'little')
    report['amfi_interface_pointer'] = pointer
    report['original_amfi_table_owner_observed'] = bool(prelink_report and any(
        e['module'] == 'com.apple.driver.AppleMobileFileIntegrity' and e['segment'] == '__DATA_CONST' and
        e['va'] <= pointer < e['va'] + e['size'] for e in prelink_report['extents']))
if args.verified_root_probe:
    report['owner_root_crypto_probe'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_native_verified_root_status', '_native_verified_root_signature_calls',
                     '_native_verified_root_block_count', '_native_verified_root_manifest_pointer', '_amfi')}
    report['owner_root_crypto_probe']['results'] = list(struct.unpack('<8I', bytes.fromhex(report['memory'][page_globals['_native_verified_root_results']])))
    report['owner_root_crypto_probe']['boot_root_authenticated'] = False
if args.follow_cache_leaf:
    entry = report.get('followed_user_entry') or {}
    leaf = leaf_record['cache_leaf_input']
    returned = entry.get('function_return', {})
    call_site = user_addresses['_cache_leaf_dispatch']
    actual_target = (returned.get('observed', False) and int(report['pc'], 16) == call_site + 4)
    executed = (actual_target and entry.get('observed', False) and int(entry['pstate'], 16) & 15 == 0 and
                entry.get('entry_bytes_after_fault', entry['entry_bytes']) == leaf['function_bytes'][:32] and
                entry.get('checkpoint', {}).get('bytes', '').startswith('c0035fd6') and
                int(returned['x0'], 16) == 0)
    report['original_cache_leaf_input'] = leaf_record
    report['original_cache_leaf_executed'] = executed
    report['original_cache_leaf_result'] = int(returned['x0'], 16) if returned.get('observed') else None
    report['original_full_cache_loaded'] = False
    report['root_authentication_solved'] = False
if args.follow_target_main:
    main = report.get('followed_main_entry') or {}
    direct_shifts = {request: int.from_bytes(bytes.fromhex(report['memory'][request]), 'little')
                     if not report['memory'][request].startswith('E') else None for request in ('fffff4025:1', 'fffff4037:1')}
    actual_target = bool(main.get('observed') and main.get('first_instruction_completed') and
        int(main['pstate'], 16) & 15 == 0 and int(main['checkpoint_pstate'], 16) & 15 == 0 and
        main['entry_bytes_after_fault'] == main_input['entry_prefix'] and main['mach_header_bytes'] == main_input['mach_header'])
    if main_fault:
        report['original_launchd_page_fault_input'] = dict(file_sha256=hashlib.sha256(main_bytes).hexdigest(),
            code_directory_hash=probe_metadata['original_cdhash'], offset=offset,
            page_sha256=hashlib.sha256(main_bytes[page:page + 4096]).hexdigest(),
            original_files_modified=False, signatures_or_trust_modified=False,
            actual_fault_applied=report.get('own_mapped_page_mutation') is not None)
    report['original_launchd_main_input'] = main_input
    report['original_launchd_main_executed'] = actual_target
    report['direct_user_commpage_shifts'] = direct_shifts
    if actual_target:
        args.break_symbol = 'original-launchd-main'
    if args.follow_display_query or args.follow_display_discovery or args.follow_display_mode or args.follow_metal_device:
        query = report.get('followed_display_query') or {}
        actual_target = actual_target and query.get('observed', False)
        if actual_target:
            args.break_symbol = 'original-default-metal-device-return' if args.follow_metal_device else 'original-display-mode-return' if args.follow_display_mode else 'original-mobile-display-discovery-epilogue' if args.follow_display_discovery else 'original-display-query-return'
report['stop_symbol'] = (args.break_symbol if actual_target else 'timeout-interrupt'
                         if report.get('bounded_timeout_interrupted') else fallback_symbols.get(int(report['pc'], 16), 'unexpected-stop'))
if has_provider:
    report['crypto14_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                                 for name in ('_source_corecrypto14_status', '_g_crypto_funcs', '_prng_ready')}
    crypto = report['crypto14_globals']
    report['crypto14_initialization_observed'] = (crypto['_source_corecrypto14_status'] == 0
                                                and bool(crypto['_g_crypto_funcs']) and crypto['_prng_ready'] == 1)
    if args.require_crypto14 and not report['crypto14_initialization_observed']:
        raise SystemExit(f'FAIL: real crypto initialization was not observed: {crypto}')
if prelink_report:
    crypto = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
              for name in ('_g_crypto_funcs', '_crypto_init', '_prng_ready')}
    report['prelinked_crypto_globals'] = crypto
    pointer = crypto['_g_crypto_funcs']
    report['original_crypto_table_owner_observed'] = any(e['module'] == 'com.apple.kec.corecrypto'
        and e['va'] <= pointer < e['va'] + e['size'] for e in prelink_report['extents'])
    report['original_crypto_initialized_observed'] = (report['original_crypto_table_owner_observed']
        and crypto['_crypto_init'] == 1 and crypto['_prng_ready'] == 1)
if has_pthread:
    report['pthread_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                                 for name in ('_source_pthread_status', '_pthread_functions', '_pthread519_pthread_kern')}
if has_native_aes:
    report['native_aes_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                                    for name in aes_globals}
if args.load_apfs:
    report['native_apfs_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                                    for name in ('_native_apfs_load_status', '_native_apfs_registered', '_native_apfs_vfsops')}
if has_iogpu_probe:
    report['native_iogpu_load_status'] = int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_iogpu_load_status']]), 'little', signed=True)
    if iogpu_component:
        iogpu_component['actual_start_observed'] = any(e['pc'] == iogpu_component['start'] for e in report['trace_events'])
        iogpu_component['original_entry_bytes_match'] = report['memory'][f'{int(iogpu_component["start"], 16):x}:10'] == iogpu_component['entry_prefix']
        report['native_iogpu_component'] = iogpu_component
if has_mobile_graphics_probe:
    report['native_mobile_graphics_load_status'] = int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_mobile_graphics_load_status']]), 'little', signed=True)
    if mobile_component:
        mobile_component['actual_start_observed'] = any(e['pc'] == mobile_component['start'] for e in report['trace_events'])
        mobile_component['original_entry_bytes_match'] = report['memory'][f'{int(mobile_component["start"], 16):x}:10'] == mobile_component['entry_prefix']
        report['native_mobile_graphics_component'] = mobile_component
if has_constant_probe:
    state = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_constants_' + name]]),
                                 'little', signed=name == 'status') for name in constant_fields}
    state.update(requested=args.constant_uploads_probe, gpu_execution_qualified=False)
    for name in constant_pointers:
        state[name] = hex(int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_constants_' + name]]), 'little'))
    state['physical'] = [hex(v) for v in struct.unpack('<6Q', bytes.fromhex(report['memory'][page_globals['_native_constants_physical']]))]
    for name, requests in constant_captures.items():
        state[name] = dict(cpu_mappings=report['kernel_range_translations'][requests['span']],
                           capture=report['indirect_memory'][requests['capture']])
    report['native_constant_uploads'] = state
if has_smmu4k_probe:
    state = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_smmu4k_' + name]]),
                                 'little', signed=name == 'status') for name in smmu4k_fields}
    state.update(requested=args.smmu4k_probe, smmu_activated=False, gpu_execution_qualified=False)
    for name in ('pool_pointer', 'data_pointer', 'cpu_mair'):
        state[name] = hex(int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_smmu4k_' + name]]), 'little'))
    state['pool_physical'] = [hex(v) for v in struct.unpack('<6Q', bytes.fromhex(report['memory'][page_globals['_native_smmu4k_pool_physical']]))]
    state['data_physical'] = [hex(v) for v in struct.unpack('<2Q', bytes.fromhex(report['memory'][page_globals['_native_smmu4k_data_physical']]))]
    for name, requests in smmu4k_captures.items():
        state[name] = dict(cpu_mappings=report['kernel_range_translations'][requests['span']],
                           chunks=[report['indirect_memory'][k] for k in requests['chunks']])
    report['native_smmu4k'] = state
if has_pm4_probe:
    report['native_adreno_pm4'] = {
        name: int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_adreno_pm4_' + name]]),
                             'little', signed=name == 'status') for name in pm4_fields}
    report['native_adreno_pm4'].update(requested=args.adreno_pm4_probe,
                                     gpu_execution_qualified=False, submission_authorized=False)
if has_adreno_probe:
    report['native_adreno_firmware'] = {
        name: int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_adreno_firmware_' + name]]),
                             'little', signed=name == 'status') for name in adreno_fields}
    adreno = report['native_adreno_firmware']
    adreno['sha256'] = report['memory'][page_globals['_native_adreno_firmware_sha256']]
    adreno['input_bytes'] = int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_adreno_firmware_image_size']]), 'little')
    adreno['requested'] = args.adreno_firmware_probe
    if args.inspect_adreno_firmware:
        adreno['input_capture'] = report['indirect_memory'][adreno_input_request]
        adreno['input_pages'] = report['kernel_range_translations'][adreno_input_range]
    adreno['gpu_execution_qualified'] = False
    adreno['firmware_authenticity_qualified'] = False
if has_mobile_client_probe:
    report['native_mobile_graphics_client'] = {
        name: int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_mobile_graphics_' + name]]),
                             'little', signed=name == 'client_init') for name in mobile_client_fields}
    report['native_mobile_graphics_client']['selector_results'] = list(struct.unpack('<3I',
        bytes.fromhex(report['memory'][page_globals['_native_mobile_graphics_client_results']])))
if block_image:
    report['native_virtio_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_native_virtio_ready', '_native_virtio_read_requests', '_native_virtio_read_failures',
                     '_native_virtio_sectors', '_native_virtio_mmio_physical')}
    report['native_virtio_first_sector_sha256'] = report['memory'][page_globals['_native_virtio_first_sector_sha256']]
if has_console:
    report['native_console_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                                       for name, _ in console_globals}
if has_gpu_broker:
    report['native_gpu_broker']={name.removeprefix('_native_gpu_broker_'):int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]),'little',signed=name.endswith('_status')) for name,_ in gpu_broker_globals}
if has_accelerator:
    report['native_accelerator']={name.removeprefix('_native_accelerator_'):int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]),'little',signed=name.endswith('_status')) for name,_ in accelerator_globals}
if has_original_client:
    report['native_original_client']={name.removeprefix('_native_original_client_'):int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]),'little',signed=name.endswith('_status')) for name,_ in original_client_globals}
if has_original_provider:
    report['native_original_provider']={name.removeprefix('_native_original_provider_'):int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]),'little',signed=name.endswith(('_status','_factory_result'))) for name,_ in original_provider_globals}
    report['native_original_provider']['frame']=list(struct.unpack('<16Q',bytes.fromhex(report['memory'][page_globals['_native_original_provider_frame']])))
    if provider_client_capture:report['native_original_provider']['factory_client_capture']=report['indirect_memory'][provider_client_capture]
if has_gpu_cpu_contexts:
    count=int.from_bytes(bytes.fromhex(report['memory'][page_globals['_native_gpu_broker_cpu_context_count']]),'little')
    if count>8:raise SystemExit('CPU context observer capacity exceeded')
    raw=bytes.fromhex(report['memory'][page_globals['_native_gpu_broker_cpu_contexts']]);contexts=[]
    for index in range(count):
        v=struct.unpack_from('<8Q',raw,index*64)
        contexts.append(dict(pid=v[0],session=v[1],TCR_EL1=hex(v[2]),TTBR0_EL1=hex(v[3]),TTBR1_EL1=hex(v[4]),SCTLR_EL1=hex(v[5]),task=hex(v[6]),native_cpu_4k_accepted=bool(v[7])))
    report['native_gpu_broker']['actual_cpu_contexts']=contexts
if has_gpu_shared_contexts:
    report['native_gpu_shared_events']={name.removeprefix('_native_gpu_shared_'):int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]),'little') for name in gpu_shared_globals}
if has_gop:
    report['native_gop_presenter'] = {name.removeprefix('_native_gop_'):int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]),'little')
                                    for name,_ in gop_globals}
if args.inspect_gop_scanout_bytes:
    expected=args.inspect_gop_scanout_bytes;video=report['actual_boot_video']['pe_video']
    if video['v_rowBytes']*video['v_height']!=expected:raise SystemExit('Actual GOP extent differs from requested inspection')
    report['gop_scanout_observation']=dict(provider='original-legacy-gop' if args.legacy_display_transfer else 'own-gop-presenter',bytes=expected,captures=[report['indirect_memory'][r] for r in gop_captures],
        translations=[report['kernel_range_translations'][r] for r in gop_spans])
if has_legacy:
    report['native_legacy_display'] = {name.removeprefix('_native_legacy_'):int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]),'little',signed=name.endswith('_status'))
                                       for name,_ in legacy_globals}
if has_legacy_client:
    report['native_legacy_properties']=bytes.fromhex(report['memory'][page_globals['_native_legacy_properties']]).split(b'\0',1)[0].decode('utf8','replace')
    report['native_legacy_client_class']=bytes.fromhex(report['memory'][page_globals['_native_legacy_client_class']]).split(b'\0',1)[0].decode('utf8','replace')
if has_ufs:
    report['native_ufs']={name.removeprefix('_native_ufs_'):int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]),'little')
                          for name,_ in ufs_globals}
if '_native_virtio_manifest_ready' in page_globals:
    report['native_virtio_integrity'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_native_virtio_manifest_ready', '_native_virtio_verified_blocks', '_native_virtio_integrity_failures',
                     '_native_virtio_verified_manifest_pointer', '_native_virtio_verified_key_pointer')}
    report['native_virtio_integrity'].update({name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                                            for name in extra_integrity_globals})
if native_hash_cache:
    report['native_signature_hash_cache'] = {
        name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_cs_native4k_hash_cache_version', '_cs_native4k_full_blocks',
                     '_cs_native4k_page_checks', '_cs_native4k_ready_blobs')}
if any(name.startswith('_armvirt_platform_') for name, _ in inspections):
    report['armvirt_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                                for name, _ in inspections if name.startswith('_armvirt_platform_')}
if any(name.startswith('_armdt_platform_') for name, _ in inspections):
    report['armdt_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                               for name, _ in inspections if name.startswith('_armdt_platform_')}
if args.armcpu:
    report['armcpu_globals'] = {name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
                               for name in ('_armcpu_registered', '_armcpu_gic_ready', '_armcpu_timer_interrupts',
                                            '_armcpu_ipi_interrupts', '_gCPUsRunning')}
    if args.smp > 1:
        report['armcpu_smp'] = {'running': int.from_bytes(bytes.fromhex(report['memory'][page_globals['_armcpu_smp_running']]), 'little'),
            'conduit': int.from_bytes(bytes.fromhex(report['memory'][page_globals['_armcpu_smp_conduit']]), 'little'),
            'step': list(struct.unpack('<8I', bytes.fromhex(report['memory'][page_globals['_armcpu_smp_step']]))),
            'psci_rc': list(struct.unpack('<8i', bytes.fromhex(report['memory'][page_globals['_armcpu_smp_psci_rc']])))}
if args.native_user:
    report['amfi_interface_pointer'] = int.from_bytes(bytes.fromhex(report['memory'][page_globals['_amfi']]), 'little')
    report['code_signing_hash_counters'] = {
        name: int.from_bytes(bytes.fromhex(report['memory'][page_globals[name]]), 'little')
        for name in ('_cs_validate_page_bad_hash', '_cs_validate_page_no_hash')}
    if prelink_report:
        pointer = report['amfi_interface_pointer']
        report['original_amfi_table_owner_observed'] = any(
            e['module'] == 'com.apple.driver.AppleMobileFileIntegrity'
            and e['segment'] == '__DATA_CONST' and e['va'] <= pointer < e['va'] + e['size']
            for e in prelink_report['extents'])
    report['native_user_memory'] = {name: report['memory'][request] for name, request in user_requests.items()}
    report['native_user_el0_observed'] = (actual_target and (args.break_symbol == '_native_user_checkpoint' or args.follow_cache_leaf)
                                          and int(report['pstate'], 16) & 15 == 0)
    if report['native_user_el0_observed']:
        pid, sysctl_result, pid_flags, sysctl_flags = struct.unpack('<4Q', bytes.fromhex(report['native_user_memory']['_results']))
        page_size = int.from_bytes(bytes.fromhex(report['native_user_memory']['_user_page_size']), 'little')
        old_length = int.from_bytes(bytes.fromhex(report['native_user_memory']['_old_length']), 'little')
        report['native_user_syscalls'] = {'pid': pid, 'sysctl_result': sysctl_result,
                                          'page_size': page_size, 'old_length': old_length,
                                          'getpid_carry': (pid_flags >> 29) & 1,
                                          'sysctl_carry': (sysctl_flags >> 29) & 1}
        report['native_user_4k_abi_observed'] = (pid == 1 and sysctl_result == 0 and page_size == 4096
                                                and old_length == 4 and not ((pid_flags | sysctl_flags) & (1 << 29)))
        if '_file_probe_results' in user_requests:
            values = struct.unpack('<10Q', bytes.fromhex(report['native_user_memory']['_file_probe_results']))
            report['native_file_probe'] = dict(zip(('open_result', 'open_nzcv', 'fcntl_result', 'fcntl_nzcv',
                'mmap_result', 'mmap_nzcv', 'native_pages_read', 'page_word_xor', 'signature_end', 'stage'), values))
        if '_cache_leaf_results' in user_requests:
            values = struct.unpack('<9Q', bytes.fromhex(report['native_user_memory']['_cache_leaf_results']))
            report['native_cache_leaf_pre_call'] = dict(zip(('open_result', 'open_nzcv', 'fcntl_result', 'fcntl_nzcv',
                'mmap_result', 'mmap_nzcv', 'stage', 'stored_return', 'stored_return_nzcv'), values))
        if '_apfs_launchd_results' in user_requests:
            values = struct.unpack('<13Q', bytes.fromhex(report['native_user_memory']['_apfs_launchd_results']))
            report['apfs_launchd_component'] = dict(zip(('mkdir', 'mkdir_nzcv', 'os_mount', 'os_mount_nzcv',
                'cache_mount', 'cache_mount_nzcv', 'chroot', 'chroot_nzcv', 'chdir', 'chdir_nzcv',
                'exec_return', 'exec_nzcv', 'stage'), values))
        if '_apfs_mount_results' in user_requests:
            values = struct.unpack('<5Q', bytes.fromhex(report['native_user_memory']['_apfs_mount_results']))
            report['native_apfs_data_mount'] = dict(zip(('mkdir_result', 'mkdir_nzcv', 'mount_result', 'mount_nzcv', 'stage'), values))
if args.check_commpage:
    report['commpage_user64_shifts'] = {name: int(report['indirect_memory'][request]['bytes'], 16)
                                        for name, request in commpage_requests.items()}
    if any(shift != 12 for shift in report['commpage_user64_shifts'].values()):
        raise SystemExit(f"Incorrect native user ABI: {report['commpage_user64_shifts']}")
(output / 'gdb-stop.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS: real UEFI -> UniXNU -> DarwinBoot -> active native 4K XNU translation')
print(json.dumps(report['kernel_page_globals'], indent=2))
if has_provider:
    print(json.dumps(report['crypto14_globals'], indent=2))
if 'armvirt_globals' in report:
    print(json.dumps(report['armvirt_globals'], indent=2))
if 'armdt_globals' in report:
    print(json.dumps(report['armdt_globals'], indent=2))
if args.armcpu:
    print(json.dumps(report['armcpu_globals'], indent=2))
if prelink_report:
    print(json.dumps(report['prelinked_crypto_globals'], indent=2))
if has_pthread:
    print(json.dumps(report['pthread_globals'], indent=2))
if args.follow_display_query or args.follow_display_discovery:
    print(f'Observed {report["stop_symbol"]}; functional iPadOS and sheng remain unverified')
elif report.get('original_launchd_main_executed'):
    print('Observed original launchd main executing at native-4K EL0; functional iPadOS and sheng remain unverified')
else:
    print(f'Observed {report["stop_symbol"]}; functional iPadOS remains unverified')
if report.get('native_file_probe'):
    print('Own file syscall probe:', json.dumps(report['native_file_probe']))
if not actual_target:
    raise SystemExit(f'Unexpected {report["stop_symbol"]} before {args.break_symbol}; inspect captured state')

if args.native_user and args.break_symbol == '_native_user_checkpoint' and not report.get('native_user_4k_abi_observed'):
    raise SystemExit('Native EL0/SVC/page-size ABI proof failed; inspect captured state')

if prelink_report and not report['original_crypto_initialized_observed']:
    raise SystemExit('The original prelinked crypto provider has not initialized')

if args.follow_cache_leaf and not report.get('original_cache_leaf_executed'):
    raise SystemExit('Original 16K-signed cache-code execution is not established')

if args.verified_root_probe and report['owner_root_crypto_probe']['_native_verified_root_status'] != 1:
    raise SystemExit('Real native owner signature and data-hash verification has not passed')
if args.break_symbol == '_native_owner_cache_checkpoint' and report['owner_cache_mount']['_native_owner_cache_status'] != 0:
    raise SystemExit('The real original SystemOS mount or owner media binding refused; inspect the actual result')
