#!/usr/bin/env python3
"""Host qualification of the native Metal frontend over the bridge (drivers/AdrenoMetal/NativeBridgeMetalFrontend.mm, bridge/NativeMetalObjects.rs).

Builds the bridge for the host, the frontend and its public-API test (bridge/frontend_host.mm), and runs the test over a host Vulkan driver given
as the runtime's loader: MoltenVK (brew install molten-vk) on this Mac. That is an offline instrument for the frontend's and the runtime's
behaviour; it says nothing of Turnip, the Adreno 740 or its SMMU. With the target's QuartzCore library on a local mount (never committed) the
test also translates it. The frontend is cross-compiled for arm64-apple-ios17.0 as well. Output stays under build/adreno-metal-frontend-host."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/adreno-metal-frontend-host'
KIT = ROOT / 'drivers/AdrenoMetal'
QUARTZCORE = ROOT / '.cache/firmware/target-volumes/os-mount/System/Library/Frameworks/QuartzCore.framework/default.metallib'
loader = next((p for p in [os.environ.get('NMB_HOST_LOADER', ''), '/opt/homebrew/lib/libMoltenVK.dylib'] if p and Path(p).is_file()), None)
if not loader:
    raise SystemExit('A host Vulkan driver is required (brew install molten-vk, or NMB_HOST_LOADER)')
subprocess.run([sys.executable, ROOT / 'scripts/build-adreno-metal-bridge.py', '--target', 'host'], check=True)
OUT.mkdir(parents=True, exist_ok=True)
flags = ['-std=c++17', '-fobjc-arc', '-O1', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-Wno-deprecated-declarations', '-I', KIT]
test = OUT / 'frontend_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/frontend_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', test], check=True)
sdk = subprocess.check_output(['xcrun', '--sdk', 'iphoneos', '--show-sdk-path'], text=True).strip()
subprocess.run(['xcrun', 'clang++', '-target', 'arm64-apple-ios17.0', '-isysroot', sdk, *flags, '-c', KIT / 'NativeBridgeMetalFrontend.mm',
                '-o', OUT / 'NativeBridgeMetalFrontend-ios.o'], check=True)
cache = OUT / 'shader-cache'
cache.mkdir(exist_ok=True)
args = [str(test), loader, str(cache), str(QUARTZCORE) if QUARTZCORE.is_file() else '']
result = subprocess.run(args, capture_output=True, text=True, timeout=1800)
(OUT / 'frontend_host.log').write_text(result.stdout + result.stderr)
lines = [l for l in result.stdout.splitlines() if l.startswith(('PASS', 'FAIL', 'QuartzCore', 'missing'))]
print('\n'.join(lines))
if result.returncode or not any(l.startswith('PASS') for l in lines):
    sys.exit('native Metal frontend host check failed (exit %d); see %s' % (result.returncode, OUT / 'frontend_host.log'))
priority_test = OUT / 'queue_priority_host'
subprocess.run(['xcrun', 'clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                KIT / 'bridge/queue_priority_host.cpp', '-o', priority_test], check=True)
subprocess.run([priority_test], check=True)
# Interface and single-sample behavior must preserve rendered pixels and queue completion.
interfaces = OUT / 'interfaces_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/interface_regressions_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-o', interfaces], check=True)
for mode in ['normal', 'single', 'default']:
    with tempfile.TemporaryDirectory(prefix='interfaces-' + mode + '-', dir=OUT) as directory:
        command = [str(interfaces), loader, directory, mode]
        run = subprocess.run(command, capture_output=True, text=True, timeout=120)
        log = OUT / ('interfaces-' + mode + '.log')
        log.write_text(run.stdout + run.stderr)
        if run.returncode or not any(line.startswith('PASS:') for line in run.stdout.splitlines()):
            sys.exit('Metal interfaces %s failed; see %s' % (mode, log))
        print(run.stdout, end='')
# Qualify compatible original UI descriptors, actual repeated blur pixels and
# independent cold archive versus driver-cache provisioning.
if QUARTZCORE.is_file():
    subprocess.run([sys.executable, ROOT / 'scripts/check-quartzcore-blur-host.py'], check=True,
                   env=dict(os.environ, NMB_HOST_LOADER=loader), timeout=660)
subprocess.run([sys.executable, ROOT / 'scripts/check-wallpaper-freeze-host.py', '--reuse-bridge'], check=True)
# A nil resource in a blit call fails the command buffer; it must not raise (an exception escaping the plugin's worker thread aborted SpringBoard).
nilargs = OUT / 'nil_args_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/nil_args_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', nilargs], check=True)
run = subprocess.run([str(nilargs), loader, str(cache)], capture_output=True, text=True, timeout=600)
(OUT / 'nil_args_host.log').write_text(run.stdout + run.stderr)
if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
    sys.exit('the nil-resource blit check failed; see %s' % (OUT / 'nil_args_host.log'))
print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
# The GPU scanout: half-float frames converted by the compute kernel store the display driver's bytes; BGRA still copies.
scanout = OUT / 'scanout_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/scanout_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', scanout], check=True)
run = subprocess.run([str(scanout), loader, str(cache)], capture_output=True, text=True, timeout=600)
(OUT / 'scanout_host.log').write_text(run.stdout + run.stderr)
if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
    sys.exit('the GPU scanout check failed; see %s' % (OUT / 'scanout_host.log'))
print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
# Interleaved encoding must be attributed to its own command buffer, regardless of commit order.
telemetry = OUT / 'telemetry_host'
subprocess.run(['xcrun', 'clang++', *flags, '-Wno-unused-function', KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/telemetry_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', telemetry], check=True)
run = subprocess.run([str(telemetry), loader, str(cache)], capture_output=True, text=True, timeout=60)
(OUT / 'telemetry_host.log').write_text(run.stdout + run.stderr)
if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
    sys.exit('per-buffer telemetry failed; see %s' % (OUT / 'telemetry_host.log'))
print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
# Render descriptors must consume binaryArchives and the strict-miss option. Use separate
# processes and initially empty caches to keep a producer's memo/disk cache out of the consumer.
archive_test = OUT / 'archive_host'
subprocess.run(['xcrun', 'clang++', *flags, '-Wno-unused-function', KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/archive_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', archive_test], check=True)
archive_log = ''
with tempfile.TemporaryDirectory(prefix='render-archive-', dir=OUT) as temporary:
    work = Path(temporary)
    for mode in ['produce', 'consume']:
        run = subprocess.run([str(archive_test), loader, str(work / (mode + '-cache')), str(work / 'render.bin'), mode],
                             capture_output=True, text=True, timeout=120)
        archive_log += run.stdout + run.stderr
        (OUT / 'archive_host.log').write_text(archive_log)
        if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
            sys.exit('render archive %s failed; see %s' % (mode, OUT / 'archive_host.log'))
        print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
# Compute creation must keep options and the same descriptor used for archive population.
compute_archive = OUT / 'compute_archive_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/compute_archive_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', compute_archive], check=True)
archive_log = ''
with tempfile.TemporaryDirectory(prefix='compute-archive-', dir=OUT) as temporary:
    work = Path(temporary)
    for mode in ['produce', 'consume']:
        run = subprocess.run([str(compute_archive), loader, str(work / (mode + '-cache')), str(work / 'compute.bin'), mode],
                             capture_output=True, text=True, timeout=120)
        archive_log += run.stdout + run.stderr
        (OUT / 'compute_archive_host.log').write_text(archive_log)
        if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
            sys.exit('compute archive %s failed; see %s' % (mode, OUT / 'compute_archive_host.log'))
        print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
# Scheduling must allow the caller to proceed before completed handlers return. A blocked handler
# makes the old waitUntilScheduled -> waitUntilCompleted alias fail deterministically, with bounded waits.
scheduled = OUT / 'scheduled_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/scheduled_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', scheduled], check=True)
run = subprocess.run([str(scheduled), loader, str(cache)], capture_output=True, text=True, timeout=30)
(OUT / 'scheduled_host.log').write_text(run.stdout + run.stderr)
if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
    sys.exit('scheduling/completion separation failed; see %s' % (OUT / 'scheduled_host.log'))
print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
resource_wait = OUT / 'resource_wait_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/resource_wait_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', resource_wait], check=True)
run = subprocess.run([str(resource_wait), loader, str(cache)], capture_output=True, text=True, timeout=60)
(OUT / 'resource_wait_host.log').write_text(run.stdout + run.stderr)
if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
    sys.exit('storage-specific resource waits failed; see %s' % (OUT / 'resource_wait_host.log'))
print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
# No-copy owners and texture ancestry must survive all actual pending uses,
# then release on completion/refusal/discard even if the command is retained.
resource_lifetime = OUT / 'resource_lifetime_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/resource_lifetime_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', resource_lifetime], check=True)
run = subprocess.run([str(resource_lifetime), loader, str(cache)], capture_output=True, text=True, timeout=30)
(OUT / 'resource_lifetime_host.log').write_text(run.stdout + run.stderr)
if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
    sys.exit('no-copy owner lifetime failed; see %s' % (OUT / 'resource_lifetime_host.log'))
print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
# Independent IOSurface imports and views must not repeat the same CPU cache
# range in one phase. The instrument forwards every real cache operation.
surface_flush = OUT / 'surface_flush_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/surface_flush_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', surface_flush], check=True)
run = subprocess.run([str(surface_flush), loader, str(cache)], capture_output=True, text=True, timeout=30)
(OUT / 'surface_flush_host.log').write_text(run.stdout + run.stderr)
if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
    sys.exit('surface cache maintenance deduplication failed; see %s' % (OUT / 'surface_flush_host.log'))
print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
# Forward every real no-copy import/release through a counting wrapper. The
# production bridge is unchanged; independently check weak reuse, GPU bytes,
# parallel creation and release after real pending completion.
surface_import_object = OUT / 'surface-import-instrumented.o'
subprocess.run(['xcrun', 'clang++', *flags, '-Dnmb_buffer_new_no_copy=tracked_surface_import',
                '-Dnmb_buffer_new_no_copy_releasing=tracked_surface_import_releasing',
                '-Dnmb_buffer_release=tracked_buffer_release', '-c', KIT / 'NativeBridgeMetalFrontend.mm',
                '-o', surface_import_object], check=True)
surface_import = OUT / 'surface_import_host'
subprocess.run(['xcrun', 'clang++', *flags, surface_import_object, KIT / 'bridge/surface_import_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', surface_import], check=True)
count_loader = OUT / 'libImportCountLoader.dylib'
subprocess.run(['xcrun', 'clang++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Werror', '-dynamiclib',
                '-I', ROOT / '.cache/mesa-work/include', KIT / 'bridge/import_count_loader.cpp', '-o', count_loader], check=True)
import_environment = dict(os.environ, NMB_TEST_REAL_VULKAN_LOADER=loader)
run = subprocess.run([str(surface_import), str(count_loader), str(cache)], env=import_environment, capture_output=True, text=True, timeout=30)
(OUT / 'surface_import_host.log').write_text(run.stdout + run.stderr)
if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
    sys.exit('live IOSurface import reuse failed; see %s' % (OUT / 'surface_import_host.log'))
print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
no_copy_import = OUT / 'no_copy_import_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/no_copy_import_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', no_copy_import], check=True)
# Cold process per mode. A bounded real-driver delay exposes the first-import
# window; raw owners and mixtures with IOSurface textures must share one import
# while retaining separate callbacks, including cross-thread callback reentry.
for mode in ('raw', 'mixed', 'reentry'):
    run = subprocess.run([str(no_copy_import), str(count_loader), str(cache), mode], env=import_environment,
                         capture_output=True, text=True, timeout=30)
    (OUT / ('no_copy_import_host-' + mode + '.log')).write_text(run.stdout + run.stderr)
    if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
        sys.exit('native no-copy import ' + mode + ' failed; see ' + str(OUT / ('no_copy_import_host-' + mode + '.log')))
    print([l for l in run.stdout.splitlines() if l.startswith('PASS')][0])
# The system's own registration (MTLAddDevice, as the target's discovery calls it for a plugin's device) accepts the device and lists it.
registered = OUT / 'register_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/register_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', registered], check=True)
run = subprocess.run([str(registered), loader, str(cache)], capture_output=True, text=True, timeout=600)
(OUT / 'register_host.log').write_text(run.stdout + run.stderr)
verdict = [l for l in run.stdout.splitlines() if l.startswith(('PASS', 'SKIP'))]
if run.returncode or not verdict:
    sys.exit('the system device registration rejected the frontend device; see %s' % (OUT / 'register_host.log'))
print(verdict[0])
# Every Metal method the target's QuartzCore references (scripts/audit-quartzcore-metal-calls.py writes the list from the unchanged target) is answered by
# the frontend's objects. Skipped when that audit has not been run on this machine (it needs the target's dyld cache, which is not in Git).
CALLS = ROOT / 'build/gpu-analysis/quartzcore-metal-calls.json'
if CALLS.is_file():
    coverage = OUT / 'selector_coverage_host'
    subprocess.run(['xcrun', 'clang++', *flags, '-Wno-unused-function', KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/selector_coverage_host.mm',
                    ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                    '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', coverage], check=True)
    run = subprocess.run([str(coverage), loader, str(cache), str(CALLS)], capture_output=True, text=True, timeout=600)
    (OUT / 'selector_coverage_host.log').write_text(run.stdout + run.stderr)
    verdict = [l for l in run.stdout.splitlines() if l.startswith(('PASS', 'GAPS'))]
    print(verdict[0] if verdict else 'selector coverage: no verdict')
    if run.returncode or not verdict or not verdict[0].startswith('PASS'):
        sys.exit('the frontend lacks Metal methods the target QuartzCore references; see %s' % (OUT / 'selector_coverage_host.log'))
# The GPU scanout presenter (GpuScanoutPresenter.h): the GPU copies a frame into scanout stand-in pages, every pixel compared, on the native frontend.
presenter = OUT / 'present_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/present_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', presenter], check=True)
run = subprocess.run([str(presenter), loader, str(cache)], capture_output=True, text=True, timeout=600)
(OUT / 'present_host.log').write_text(run.stdout + run.stderr)
if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
    sys.exit('the GPU scanout presenter host check failed; see %s' % (OUT / 'present_host.log'))
print('PASS: GPU scanout presenter over the native frontend: ' + ', '.join(l.split(' ', 1)[1] for l in run.stdout.splitlines() if l.startswith('ok')))
# The plugin's bridge phase in order over the host simulation (scripts/check-turnip-darwin-host.py builds it): self-test, then the frontend on
# a second Turnip device. Results are not checked there (the software CP executes nothing); every step must run and retire.
HOSTSIM = ROOT / 'build/turnip-darwin-host/libhostiokit.dylib'
HOST_TURNIP = ROOT / 'build/mesa-tu/src/freedreno/vulkan/libvulkan_freedreno.dylib'
if not HOSTSIM.is_file() or not HOST_TURNIP.is_file():
    sys.exit('Build the host simulation first: python3 scripts/check-turnip-darwin-host.py')
# The target's default compute-function path must reuse both translated artifacts
# and real Turnip application pipeline records across processes, with no archive.
driver_cache = OUT / 'driver_cache_host'
subprocess.run(['xcrun', 'clang++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Werror',
                '-I', KIT / 'bridge', KIT / 'bridge/driver_cache_host.cpp',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', driver_cache], check=True)
cache_env = {k: v for k, v in os.environ.items() if not k.startswith(('IR3_', 'FD_MESA_', 'NIR_', 'TU_', 'HOSTSIM_', 'MESA_', 'METAL2VULKAN_'))}
cache_env.update(DYLD_INSERT_LIBRARIES=str(HOSTSIM), MESA_SHADER_CACHE_DISABLE='true', MESA_LOG='')
with tempfile.TemporaryDirectory(prefix='runtime-driver-cache-', dir=OUT) as temporary:
    for mode in ['produce', 'consume']:
        run = subprocess.run([str(driver_cache), str(HOST_TURNIP), temporary, mode], env=cache_env,
                             capture_output=True, text=True, timeout=180)
        log = OUT / ('runtime-driver-cache-' + mode + '.log')
        log.write_text(run.stdout + run.stderr)
        if run.returncode or not any(l.startswith('PASS:') for l in run.stdout.splitlines()):
            sys.exit('default compute cache %s failed; see %s' % (mode, log))
        print(run.stdout, end='')
sequence = OUT / 'plugin_sequence_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/plugin_sequence_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-o', sequence], check=True)
hostcache = OUT / 'hostsim-cache'
hostcache.mkdir(exist_ok=True)
env = dict(os.environ, DYLD_INSERT_LIBRARIES=str(HOSTSIM), MESA_LOG='', TU_DEBUG='nocb')
env.pop('TU_DARWIN_SERVICE', None)
run = subprocess.run([str(sequence), str(HOST_TURNIP), str(hostcache)], env=env, capture_output=True, text=True, timeout=1800)
(OUT / 'plugin_sequence_host.log').write_text(run.stdout + run.stderr)
summary = [l for l in run.stdout.splitlines() if l.startswith(('selftest', 'frontend'))]
print('\n'.join(summary))
if run.returncode or not any(l.startswith('selftest code 0 ') for l in summary) or not any(l.endswith('last 660f') for l in summary):
    sys.exit('the plugin bridge phase did not run through on the host simulation; see %s' % (OUT / 'plugin_sequence_host.log'))
print('PASS: plugin bridge phase over the host simulation: self-test, second device, every frontend step submitted and retired (results unchecked)')
# As the tablet allocates: every non-contiguous BO one physical page per span, and no contiguous run above 8 MiB, so the runtime's 64 MiB
# blocks come back scattered (int-070 failed the render step there with OutOfMemory(Device) when the VM's span table was full).
scatter_env = dict(env, HOSTSIM_SCATTER='1', HOSTSIM_CONTIGUOUS_MAX=str(8 << 20))
run = subprocess.run([str(sequence), str(HOST_TURNIP), str(hostcache)], env=scatter_env, capture_output=True, text=True, timeout=1800)
(OUT / 'plugin_sequence_scatter.log').write_text(run.stdout + run.stderr)
summary = [l for l in run.stdout.splitlines() if l.startswith(('selftest', 'frontend'))]
print('\n'.join(summary))
if run.returncode or not any(l.startswith('selftest code 0 ') for l in summary) or not any(l.endswith('last 660f') for l in summary):
    sys.exit('the plugin bridge phase failed with scattered BOs; see %s' % (OUT / 'plugin_sequence_scatter.log'))
print('PASS: the same phase with scattered single-page spans and no contiguous run above 8 MiB (results unchecked)')
# Core Image over the frontend, and the Core Image kernel library's answers Apple's Metal gives (no function names, a kernel by name of
# function type 4): iPadOS 27's Core Image takes its DAG kernels so.
coreimage = OUT / 'coreimage_host'
subprocess.run(['xcrun', 'clang++', *flags, KIT / 'NativeBridgeMetalFrontend.mm', KIT / 'bridge/coreimage_host.mm',
                ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a', '-framework', 'Foundation', '-framework', 'Metal',
                '-framework', 'IOSurface', '-framework', 'CoreFoundation', '-framework', 'CoreImage', '-framework', 'CoreGraphics',
                '-o', coreimage], check=True)
kernels = '/System/Library/Frameworks/CoreImage.framework/Versions/A/Resources/ci_stdlib.metallib'
cicache = OUT / 'coreimage-cache'
cicache.mkdir(exist_ok=True)
for name, extra in [('apple', {'NMB_SYSTEM_DEVICE': '1'}), ('frontend', {})]:
    run = subprocess.run([str(coreimage), loader, str(cicache), kernels], env=dict(os.environ, **extra), capture_output=True, text=True, timeout=600)
    (OUT / ('coreimage_%s.log' % name)).write_text(run.stdout + run.stderr)
    if run.returncode or not any(l.startswith('PASS') for l in run.stdout.splitlines()):
        sys.exit('Core Image over the %s device failed; see %s' % (name, OUT / ('coreimage_%s.log' % name)))
print('PASS: Core Image renders over the frontend; its kernel library answers as Apple\'s Metal does')
