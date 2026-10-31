#!/usr/bin/env python3
"""Build the native Metal bridge (drivers/AdrenoMetal/bridge/NativeMetalBridge.rs): the pinned metal2vulkan runtime behind a C ABI, as a static library.

--target ios (default) cross-builds for arm64-apple-ios17.0, --target ios27 for arm64e-apple-ios27.0 (nightly, std built from source), --target host for the macOS host simulation. The runtime's own example library
(runtime_examples.ll) and its function-constant fixture are assembled to AIR with llvm-as and embedded for the self-tests. Only generated build files hold local paths; nothing here
is committed. Output: build/adreno-metal-bridge/<target>/libadreno_metal_bridge.a"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / 'scripts/data/gpu-metal-vulkan-inputs.json').read_text())['translator']['commit']
SOURCE = ROOT / '.cache/gpu-reference/metal2vulkan'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--target', choices=['ios', 'ios27', 'host'], default='ios')
parser.add_argument('--manifest-only', action='store_true',
                    help='write build/adreno-metal-bridge/Cargo.toml (patched source, fixtures) and stop before cargo, for `cargo fetch`')
args = parser.parse_args()
if subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip() != PIN:
    raise SystemExit('Translator revision differs from the qualified source pin')
PATCHES = [ROOT / 'drivers/AdrenoMetal/bridge/patches' / name for name in [
    # Each stacks on the source the ones before it leave.
    '0001-optional-constant-output-members.patch', '0002-resource-wait-storage-dependencies.patch',
    '0003-cache-device-entry-point-priming.patch', '0004-fold-constant-global-field-loads.patch',
    # A draw whose pipeline the driver refused binds nothing (int-170: tu_CmdBindPipeline in the render server).
    '0005-skip-draws-without-a-pipeline.patch',
    # A batch's barrier globals on the stack, and the neutral resources' maps by the runtime's key hash.
    '0006-batch-barriers-and-key-hash-neutral-maps.patch',
    # From the DroidVM board's translator patches: a cache directory a sandboxed process may not write, llvm.bitreverse, a patch
    # function with no control points, and Core Image kernel libraries (file_type 1) loaded as Metal loads them.
    '0007-optional-shader-cache-directory.patch', '0008-llvm-bitreverse.patch', '0009-patch-with-no-control-points.patch',
    '0010-core-image-kernel-libraries.patch',
    # A two-plane surface's shadow starts as its memory lies; the Astronomy wallpaper's extended-range sRGB blends take the rounded
    # model; pooled blocks start at 4 MiB and grow (the render server alone held 1 GiB of wired memory).
    '0011-two-plane-shadow-as-memory-lies.patch', '0012-srgb-extended-range-blend-rounded-model.patch',
    '0013-growing-memory-blocks.patch',
    # HostPageTexturePolicy::InPlaceWrites: textures over surfaces and padded buffers are images over their bytes, rendered and written
    # too, where their tile stores stay within their rows, instead of shadows copied in and out every pass.
    '0014-in-place-written-textures.patch', '0015-in-place-written-host-page-textures.patch',
    # Device::refuse_rebinds: no call logs or per-command holds of no-copy buffers, which only a rebind or a detach reads.
    '0016-refuse-rebinds.patch',
    # A heap texture's own-device answer rounded up to a multiple of its alignment, as Metal's answers are: a heap sized as the sum of
    # its textures' answers then holds them (iconservicesagent's Core Image heaps ran out: OutOfMemory(Heap)).
    '0017-heap-texture-size-a-multiple-of-its-alignment.patch',
    # The runtime's live device memory in bytes by kind (pooled, placed, empty kept, dedicated, imported), for the frontend's MEM row.
    '0018-memory-census-bytes.patch',
    # The call stacks that allocated device memory of 4 MiB or more, by bytes, for the frontend's MA rows.
    '0019-allocation-sites.patch',
    # A written texture over host pages stays in place at any size: Turnip loads and stores a linear host image of partial tile blocks
    # over its texels alone (patches/mesa/turnip-render-mode-for-attachment-memory.patch); its shadow merged every pass back through 94 MB.
    '0020-written-host-page-textures-in-place-at-any-size.patch',
    # A dedicated block of images whose image went stays spare for the next one of its pool (Core Animation's memoryless attachments,
    # backed at their first pass, were each a new 40-112 MiB allocation), freed after 10 s, when a block cannot be made, or under memory
    # pressure; room in the pools is kept by a thread of the device's, not in the creation call that asked for it.
    '0021-spare-image-blocks-and-room-keeper.patch',
    # stage_trace.rs: each command buffer's stages from its commit to its completion (commit, lowering, recording, the scheduler's
    # holds, each submission, the completion waiter) and the scheduler's sleeps and wakes, read by the frontend (nmb_stage_ring_read).
    '0022-command-buffer-stage-trace.patch']]


def git_tree(*steps):
    # The source tree a scratch index holds after HEAD and the given commands, without touching the source's own index.
    index = ROOT / 'build/adreno-metal-bridge-index'
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    subprocess.run(['git', '-C', str(SOURCE), 'read-tree', 'HEAD'], env=env, check=True)
    for step in steps:
        subprocess.run(['git', '-C', str(SOURCE)] + step, env=env, check=True)
    tree = subprocess.check_output(['git', '-C', str(SOURCE), 'write-tree'], env=env, text=True).strip()
    index.unlink()
    return tree


# The tree after each prefix of the recorded patches; the source must be one of them.
states = [git_tree(*[['apply', '--cached', str(patch)] for patch in PATCHES[:count]]) for count in range(len(PATCHES) + 1)]
current = git_tree(['add', '-A'])
if current not in states:
    raise SystemExit('Translator source differs from the pinned revision plus its recorded patches')
for patch in PATCHES[states.index(current):]:
    subprocess.run(['git', '-C', str(SOURCE), 'apply', str(patch)], check=True)
if git_tree(['add', '-A']) != states[-1]:
    raise SystemExit('Translator patch result differs from its exact recorded source')
out = ROOT / 'build/adreno-metal-bridge'
out.mkdir(parents=True, exist_ok=True)
llvm_as = next((p for p in ['/opt/homebrew/opt/llvm/bin/llvm-as', shutil.which('llvm-as') or ''] if p and Path(p).exists()), None)
if not llvm_as:
    raise SystemExit('llvm-as (LLVM 21 or newer) is required to assemble the fixture')
air = out / 'runtime_examples.air'
subprocess.run([llvm_as, '-o', air, SOURCE / 'crates/metal2vulkan-validation/fixtures/public/examples/runtime_examples.ll'], check=True)
fc_air = out / 'function_constant.air'
subprocess.run([llvm_as, '-o', fc_air, SOURCE / 'crates/metal2vulkan-validation/fixtures/public/kernel_function_constant_gate_fold.ll'], check=True)
# The GPU scanout's half-float conversion kernel (GpuScanoutPresenter.h), hand-written AIR.
scanout_air = out / 'scanout_convert.air'
subprocess.run([llvm_as, '-o', scanout_air, ROOT / 'drivers/AdrenoMetal/shaders/scanout_convert.ll'], check=True)
manifest = out / 'Cargo.toml'
manifest.write_text('\n'.join([
    '[package]', 'name = "adreno-metal-bridge"', 'version = "0.1.0"', 'edition = "2024"', 'rust-version = "1.98"', '[workspace]',
    '[lib]', 'crate-type = ["staticlib"]', 'path = ' + json.dumps(str(ROOT / 'drivers/AdrenoMetal/bridge/NativeMetalBridge.rs')),
    '[dependencies]',
    'metal2vulkan = { path = ' + json.dumps(str(SOURCE / 'crates/metal2vulkan')) + ', features = ["ash"] }',
    'metal2vulkan-runtime = { path = ' + json.dumps(str(SOURCE / 'crates/metal2vulkan-runtime')) + ' }',
    'libc = "0.2"',
    # The runtime hashes every shader-cache key and entry; without asm, sha2 0.10 on aarch64 is the portable software rounds, not the
    # ARMv8 SHA-256 instructions every target CPU has (cpufeatures answers sha2 true on Apple platforms).
    'sha2 = { version = "0.10", features = ["asm"] }',
    # The render server's display thread spends most of a frame in the runtime, much of it in small functions across the
    # translator's crates: one optimisation unit with link-time optimisation lets them inline across crate boundaries.
    '[profile.release]', 'panic = "unwind"', 'debug = 1', 'lto = "fat"', 'codegen-units = 1', '',
]))
if args.manifest_only:
    print(manifest)
    raise SystemExit(0)
triple = {'ios': 'aarch64-apple-ios', 'ios27': 'arm64e-apple-ios', 'host': 'aarch64-apple-darwin'}[args.target]
# arm64e has no prebuilt std: it is built from rust-src (RUSTC_BOOTSTRAP for -Z); the iPadOS 27 processes that load the plugin are arm64e.
cargo = ['cargo', '+1.98.0'] + (['-Z', 'build-std=std,panic_unwind'] if args.target == 'ios27' else [])
# The translator source the runtime is built from (its pin and recorded patches), which keys the shader cache: shader priming keeps what it
# finished while this stays the same (PrimeShaders.h).
runtime_id = hashlib.sha256((PIN + '\n' + states[-1]).encode()).hexdigest()[:32]
env = dict(os.environ, NMB_RUNTIME_ID=runtime_id, NMB_FIXTURE_AIR=str(air), NMB_FC_AIR=str(fc_air), NMB_SCANOUT_AIR=str(scanout_air), IPHONEOS_DEPLOYMENT_TARGET='27.0' if args.target == 'ios27' else '17.0', MACOSX_DEPLOYMENT_TARGET='14.0')
if args.target == 'ios27':
    env['RUSTC_BOOTSTRAP'] = '1'
target_dir = ROOT / 'build/m2v-target'
log = out / ('build-%s.log' % args.target)
with log.open('w') as stream:
    result = subprocess.run(cargo + ['build', '--release', '--manifest-path', manifest, '--target', triple,
                             '--target-dir', target_dir], env=env, stdout=stream, stderr=subprocess.STDOUT, timeout=1800)
if result.returncode:
    raise SystemExit(log.read_text()[-6000:])
library = target_dir / triple / 'release/libadreno_metal_bridge.a'
final = out / args.target / 'libadreno_metal_bridge.a'
final.parent.mkdir(exist_ok=True)
shutil.copyfile(library, final)
print('PASS: native Metal bridge static library for %s (%d bytes); translator %s' % (args.target, final.stat().st_size, PIN[:12]))
