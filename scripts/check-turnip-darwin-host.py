#!/usr/bin/env python3
"""Drive the Turnip darwin backend through a real Vulkan instance against the host copy of the NativeAdreno kernel stack.

The kernel half is the real GPU context bring-up, VM, ring, submit and user-client code over software SMMU/CP peers
(tests/hostsim/host_gpu_service.cpp); an IOKit shim answers the backend's IOKit calls. Nothing here runs a shader or touches
hardware: the software CP retires every submission at once. Needs the host Turnip build (build-turnip-darwin.py --target host)."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
kit = ROOT / 'drivers/Adreno740'
sim = kit / 'tests/hostsim'
out = ROOT / 'build/turnip-darwin-host'
out.mkdir(parents=True, exist_ok=True)
smmu = ROOT / 'kits/ArmSmmu4K'
library = ROOT / 'build/mesa-tu/src/freedreno/vulkan/libvulkan_freedreno.dylib'
if not library.exists():
    sys.exit('Build the host Turnip first: python3 scripts/build-turnip-darwin.py --target host')

includes = out / 'host-include'
for name in ['IOKit/IOTypes.h', 'IOKit/IOReturn.h', 'IOKit/IOBufferMemoryDescriptor.h', 'IOKit/IOLib.h', 'kern/task.h']:
    path = includes / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#include "XnuMemoryFixture.h"\n')
resource_private = includes / 'sys/resource_private.h'
resource_private.parent.mkdir(parents=True, exist_ok=True)
resource_private.write_text(
    '#pragma once\n'
    '#define PRIO_DARWIN_GPU 5\n'
    '#define PRIO_DARWIN_GPU_UNKNOWN 0x0\n'
    '#define PRIO_DARWIN_GPU_ALLOW 0x1\n'
    '#define PRIO_DARWIN_GPU_DENY 0x2\n'
    '#define PRIO_DARWIN_GPU_BACKGROUND 0x3\n'
    '#define PRIO_DARWIN_GPU_UTILITY 0x4\n'
    '#define PRIO_DARWIN_GPU_UI_NON_FOCAL 0x5\n'
    '#define PRIO_DARWIN_GPU_UI 0x6\n'
    '#define PRIO_DARWIN_GPU_UI_FOCAL 0x7\n'
)

objects = []
for stem in ['ArmSmmu4KContext', 'ArmSmmu4KProgram', 'ArmSmmu4KLive', 'ArmSmmu4KStreams', 'ArmSmmu4KMmio']:
    obj = out / (stem + '.o')
    subprocess.run(['xcrun', 'clang', '-std=c11', '-O1', '-fPIC', '-c', smmu / (stem + '.c'), '-o', obj], check=True)
    objects.append(obj)
obj = out / 'AdrenoPM4.o'
subprocess.run(['xcrun', 'clang', '-std=c11', '-O1', '-fPIC', '-c', ROOT / 'kits/AdrenoPM4/AdrenoPM4.c', '-o', obj], check=True)
objects.append(obj)

service = out / 'host_gpu_service.o'
subprocess.run(['xcrun', 'clang++', '-std=c++23', '-O1', '-fPIC', '-I', includes, '-I', sim.parent, '-I', kit, '-I', smmu,
                '-I', ROOT / 'kits/AdrenoPM4', '-c', sim / 'host_gpu_service.cpp', '-o', service], check=True)
core = []
for name in ['NativeAdrenoMemory', 'NativeAdrenoSmmuMemory', 'NativeAdrenoVm', 'NativeAdrenoRing', 'NativeAdrenoSubmit',
             'NativeAdrenoUserClient', 'NativeAdrenoTimer', 'NativeAdrenoSmmuContext', 'NativeAdrenoGpuContext',
             'NativeAdrenoPreempt', 'tests/HostKernelHooks']:
    obj = out / (Path(name).name + '.o')
    subprocess.run(['xcrun', 'clang++', '-std=c++23', '-O1', '-fPIC', '-I', includes, '-I', sim.parent, '-I', kit, '-I', smmu,
                    '-I', ROOT / 'kits/AdrenoPM4', '-c', kit / (name + '.cpp'), '-o', obj], check=True)
    core.append(obj)
shim_obj = out / 'host_iokit_shim.o'
subprocess.run(['xcrun', 'clang++', '-std=c++17', '-O1', '-fPIC', '-c', sim / 'host_iokit_shim.cpp', '-o', shim_obj], check=True)
shim = out / 'libhostiokit.dylib'
subprocess.run(['xcrun', 'clang++', '-dynamiclib', '-o', shim, service, shim_obj, *core, *objects,
                '-framework', 'IOKit', '-framework', 'CoreFoundation'], check=True)
smoke = out / 'vulkan_smoke'
subprocess.run(['xcrun', 'clang', '-std=c11', '-O1', '-I', '/opt/homebrew/include', sim / 'vulkan_smoke.c', '-o', smoke,
                '-Wl,-rpath,' + str(out)], check=True)

plugin_smoke = out / 'plugin_smoke'
subprocess.run([sys.executable, ROOT / 'scripts/gen-turnip-smoke-shaders.py'], check=True)
subprocess.run(['xcrun', 'clang++', '-std=c++17', '-O1', '-I', ROOT / 'drivers/AdrenoMetal', '-I', ROOT / '.cache/mesa-work/include',
                '-I', ROOT / 'build/turnip-smoke',
                sim / 'plugin_smoke.cpp', '-o', plugin_smoke], check=True)
env = dict(os.environ, DYLD_INSERT_LIBRARIES=str(shim), MESA_LOG='')
env.pop('TU_DARWIN_SERVICE', None)   # the default is the production transport: accelerator service, open type 0x4147, tunnel through one admitted selector
result = subprocess.run([str(smoke), str(library)], env=env, capture_output=True, text=True, timeout=300)
(out / 'smoke.log').write_text(result.stdout + result.stderr)
print(result.stdout, end='')
if result.stderr.strip():
    print(result.stderr[-3000:], end='')
if result.returncode or 'PASS' not in result.stdout:
    sys.exit('Turnip darwin host smoke failed (exit %d); see %s' % (result.returncode, out / 'smoke.log'))
# Keep a software ring fence pending while freeing an unrelated mapped allocation.
# The actual KMD must defer native handle/view/IOVA retirement, bound pressure waits,
# and preserve ownership on failures. This exercises real transport code, not pixels.
deferred = out / 'deferred_bo'
subprocess.run(['xcrun', 'clang++', '-std=c++23', '-O1', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
                '-I', '/opt/homebrew/include', '-I', kit, sim / 'deferred_bo.cpp', '-o', deferred], check=True)
deferred_env = dict(env, TU_DARWIN_RETIRE_TRACE='1')
deferred_env.pop('HOSTSIM_FAIL_USER_UNMAP', None)
for mode in ['normal', 'busy', 'fence-error', 'free-error', 'lease-error', 'view-error', 'map-cleanup-error', 'pressure']:
    # The release paths need every free to reach the kernel: only the normal mode runs with the BO cache on.
    mode_env = dict(deferred_env, TU_DARWIN_BO_CACHE='1' if mode == 'normal' else '0')
    test = subprocess.run([str(deferred), str(library), mode], env=mode_env, capture_output=True, text=True, timeout=60)
    (out / ('deferred-' + mode + '.log')).write_text(test.stdout + test.stderr)
    verdict = [line for line in test.stdout.splitlines() if line.startswith('PASS:')]
    if test.returncode or not verdict:
        sys.exit('Deferred BO %s failed (exit %d); see %s' % (mode, test.returncode, out / ('deferred-' + mode + '.log')))
    if mode == 'pressure' and 'pressure=0' not in test.stderr:
        sys.exit('Deferred BO pressure control waited for the GPU instead of growing its queue')
    print(verdict[0])
# Driver cache controls compile Adreno code but submit/execute no shader.
subprocess.run([sys.executable, ROOT / 'scripts/check-turnip-pipeline-cache-host.py'], check=True)
# Original UI recipes additionally cover graphics-library caches, strict driver
# feedback and genuine UUID/empty-cache refusals. The software peer runs no shader.
quartzcore_check = ROOT / 'scripts/check-quartzcore-turnip-cache-host.py'
if quartzcore_check.is_file():
    with tempfile.TemporaryDirectory(prefix='quartzcore-driver-cache-', dir=out) as temporary:
        subprocess.run([sys.executable, quartzcore_check,
                        '--output', Path(temporary) / 'control'], check=True, timeout=660)

bridge_archive = ROOT / 'build/adreno-metal-bridge/host/libadreno_metal_bridge.a'
if bridge_archive.is_file() and shutil.disk_usage(ROOT).free > 5 * 1024**3 + 256 * 1024**2:
    with tempfile.TemporaryDirectory(prefix='priming-driver-cache-', dir=out) as temporary:
        subprocess.run([sys.executable, ROOT / 'scripts/check-priming-cache-host.py',
                        '--output', Path(temporary) / 'control'], check=True, timeout=360)

env_plugin = dict(env)
plugin = subprocess.run([str(plugin_smoke), str(library)], env=env_plugin, capture_output=True, text=True, timeout=300)
(out / 'plugin_smoke.log').write_text(plugin.stdout + plugin.stderr)
print(plugin.stdout, end='')
if plugin.returncode:
    sys.exit('The plugin Turnip sequence did not behave as expected on the host (exit %d); see %s' % (plugin.returncode, out / 'plugin_smoke.log'))
# Watchdog: block the first BoAlloc for 17 s; the 15 s sample must name the last marker (6004), show the worker waiting (not running) and
# carry at least one return address inside the Turnip image ('v' frames).
stalled = subprocess.run([str(plugin_smoke), str(library)], env=dict(env_plugin, HOSTSIM_STALL='17'), capture_output=True, text=True, timeout=300)
(out / 'plugin_watchdog.log').write_text(stalled.stdout + stalled.stderr)
lines = [l for l in stalled.stdout.splitlines() if l.startswith('watchdog: W ')]
print('\n'.join(lines))
if stalled.returncode or len(lines) != 1 or not lines[0].startswith('watchdog: W 6004 ') or ' v' not in lines[0] or 'kern' in lines[0]:
    sys.exit('The plugin watchdog did not sample the stalled worker as expected; see %s' % (out / 'plugin_watchdog.log'))
print('PASS: the plugin watchdog sampled a worker blocked in vkCreateDevice (one line, marker 6004, frames inside Turnip)')
print('PASS: the plugin Turnip sequence (fill, compute pipeline, render pass) built, submitted and retired every command buffer over the host kernel stack (the software CP executes nothing, so no result is verified by design)')
print('PASS: Turnip darwin backend drove a Vulkan instance, device, memory mapping and a submission over the host kernel stack; no GPU')
