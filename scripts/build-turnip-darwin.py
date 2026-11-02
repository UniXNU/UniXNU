#!/usr/bin/env python3
"""Build Turnip (Mesa freedreno Vulkan) with the native Darwin kernel backend (patches/mesa/turnip-darwin-kmd.patch).

--target host builds for the Mac only to prove the backend compiles and links against the real Turnip; --target ios
cross-builds the ARM64/iOS 17 library, --target ios27 the arm64e/iOS 27 one. Neither runs a GPU: the backend talks to the NativeAdreno IOKit service, which
exists only on the tablet. Output stays under build/ and is never committed."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from mesa_patch_identity import validate_recorded_patches

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--target', choices=('host', 'ios', 'ios27'), default='host')
parser.add_argument('--configure-only', action='store_true')
parser.add_argument('--builtin-pack', type=Path, help='Embed an exact-source/profile/GPU-bound own builtin pack; no runtime compiler fallback')
args = parser.parse_args()
SOURCE = ROOT / '.cache/mesa-work'
OUT = ROOT / {'host': 'build/mesa-tu', 'ios': 'build/mesa-tu-ios', 'ios27': 'build/mesa-tu-ios27'}[args.target]
LOGS = ROOT / '.cache'


def read(cmd):
    return subprocess.check_output([str(c) for c in cmd], text=True).strip()


pins = json.loads((ROOT / 'scripts/data/adreno-compiler-inputs.json').read_text())
if read(['git', '-C', SOURCE, 'rev-parse', 'HEAD']) != pins['mesa']['commit']:
    sys.exit('Pinned Mesa source differs')
validate_recorded_patches(ROOT, SOURCE, pins)
if not shutil.which('glslangValidator'):
    sys.exit('glslangValidator is required by the Vulkan runtime build (brew install glslang)')

env = {k: v for k, v in os.environ.items() if not k.startswith(('IR3_', 'FD_MESA_', 'NIR_', 'MESA_SHADER_', 'TU_'))}
env['PATH'] = str(ROOT / '.cache/mesa-tools/bin') + ':' + str(ROOT / '.cache/mesa-venv/bin') + ':' + env['PATH']
options = ['-Dgallium-drivers=', '-Dvulkan-drivers=freedreno', '-Dfreedreno-kmds=darwin',
           '-Dtu-darwin-abi-dir=' + str(ROOT / 'drivers/Adreno740'), '-Dplatforms=macos', '-Dglx=disabled',
           '-Degl=disabled', '-Dgbm=disabled', '-Dopengl=false', '-Dgles1=disabled', '-Dgles2=disabled',
           '-Dllvm=disabled', '-Dshared-glapi=disabled', '-Dxmlconfig=disabled', '-Dshader-cache=enabled',
           '-Dtools=', '-Dbuild-tests=false', '-Dvideo-codecs=', '-Dvulkan-layers=']
setup = [ROOT / '.cache/mesa-venv/bin/meson', 'setup', OUT, SOURCE, '--wrap-mode=nodownload']
if args.target in ('ios', 'ios27'):
    sdk = read(['xcrun', '--sdk', 'iphoneos', '--show-sdk-path'])
    find = lambda tool: read(['xcrun', '--sdk', 'iphoneos', '--find', tool])
    triple = 'arm64e-apple-ios27.0' if args.target == 'ios27' else 'arm64-apple-ios17.0'
    flags = ['-target', triple, '-isysroot', sdk, '-fstack-protector-strong']
    cross = ROOT / ('build/mesa-tu-%s.cross' % args.target)
    cross.parent.mkdir(exist_ok=True)
    cross.write_text(
        '[binaries]\nc = %r\ncpp = %r\nobjc = %r\nar = %r\nstrip = %r\npkg-config = \'/usr/bin/false\'\n'
        % (find('clang'), find('clang++'), find('clang'), find('ar'), find('strip')) +
        "[host_machine]\nsystem = 'darwin'\ncpu_family = 'aarch64'\ncpu = 'arm64'\nendian = 'little'\n"
        "[properties]\nneeds_exe_wrapper = true\n[built-in options]\n" +
        ''.join('%s = %r\n' % (k, flags) for k in ('c_args', 'cpp_args', 'objc_args', 'c_link_args', 'cpp_link_args',
                                                    'objc_link_args')))
    setup += ['--cross-file', cross]
    # Release with NDEBUG for the tablet: Mesa's default debugoptimized keeps assertions and NIR validation after
    # every pass, which the tablet's pipeline makings paid for (int-143: 58 pipeline states took 68 s). The host
    # build keeps them for the simulation checks.
    options += ['-Dlibunwind=disabled', '-Dlmsensors=disabled', '-Dvalgrind=disabled', '-Dexpat=disabled',
                '-Dzstd=disabled', '-Dbuildtype=release', '-Db_ndebug=true']
    env.update(CC=find('clang'), CXX=find('clang++'), CFLAGS='', CXXFLAGS='', CPPFLAGS='', LDFLAGS='')
else:
    env.update(CC='/usr/bin/clang', CXX='/usr/bin/clang++')
# Bind raw variant layout and code to every actual source edit, untracked
# source addition, compiler, target and build option. The generated embedded
# header stays outside SOURCE and is deliberately excluded from this key;
# otherwise the pack would make its own producer identity circular.
source_diff = subprocess.check_output(['git', '-C', SOURCE, 'diff', 'HEAD', '--binary'])
untracked = subprocess.check_output(['git', '-C', SOURCE, 'ls-files', '--others', '--exclude-standard', '-z']).split(b'\0')
source_extras = {name.decode(): hashlib.sha256((SOURCE / name.decode()).read_bytes()).hexdigest()
                 for name in untracked if name and (SOURCE / name.decode()).is_file()}
profile = dict(mesa_revision=pins['mesa']['commit'], target=args.target,
               source_diff_sha256=hashlib.sha256(source_diff).hexdigest(), extra_sources=source_extras,
               patch_guard_sha256=hashlib.sha256((ROOT / 'scripts/mesa_patch_identity.py').read_bytes()).hexdigest(),
               compiler=read([env['CXX'], '--version']), options=options,
               build_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
source_id = hashlib.sha256(json.dumps(profile, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
OUT.mkdir(parents=True, exist_ok=True)
pack_header = ''
pack_sha = None
if args.builtin_pack:
    pack = args.builtin_pack.resolve().read_bytes()
    if not 112 <= len(pack) <= 4 * 1024**2 or pack[:8] != b'TUBUILT1' or pack[16:80] != source_id.encode():
        sys.exit('Builtin pack is not from this exact compiler source/profile; regenerate rather than relabel it')
    header = OUT / 'tu_builtin_pack.generated.h'
    header.write_text('/* Generated own compiler output: never commit. */\nstatic const unsigned char tu_builtin_pack_bytes[] = {\n' +
                      ''.join(','.join('0x%02x' % b for b in pack[i:i+16]) + ',\n' for i in range(0,len(pack),16)) + '};\n')
    pack_header = str(header)
    pack_sha = hashlib.sha256(pack).hexdigest()
(OUT / 'builtin-build-profile.json').write_text(json.dumps(dict(source_id=source_id, profile=profile,
    embedded_pack_sha256=pack_sha, builtin_pack_required=bool(args.builtin_pack)), indent=2) + '\n')
options += ['-Dtu-builtin-source-id=' + source_id, '-Dtu-builtin-pack-header=' + pack_header]
# The pipeline cache's identity (VkPhysicalDeviceProperties::pipelineCacheUUID) from the compiler's source alone, the same for every
# target: Mesa's own on Darwin is the library file's mtime (disk_cache_get_function_timestamp), which differs per install and per build,
# so the pipelines a boot compiled into the persistent Data cache would miss after every image rebuild of the same compiler.
build_id = hashlib.sha256(json.dumps(dict(mesa_revision=pins['mesa']['commit'], source_diff_sha256=profile['source_diff_sha256'],
                                          extra_sources=source_extras), sort_keys=True).encode()).hexdigest()[:40]
options += ['-Dtu-build-id=' + build_id]
log = LOGS / ('mesa-tu-%s-configure.log' % args.target)
with log.open('w') as stream:
    # An existing build directory takes the current options (meson configure), so an option added here reaches it.
    command = setup + options if not (OUT / 'build.ninja').exists() else [ROOT / '.cache/mesa-venv/bin/meson', 'configure', OUT] + options
    if subprocess.run([str(c) for c in command], env=env, stdout=stream, stderr=subprocess.STDOUT).returncode:
        sys.exit('Configure failed; see ' + str(log) + '\n' + '\n'.join(log.read_text().splitlines()[-12:]))
if args.configure_only:
    print('PASS: Turnip darwin-kmd configuration (%s)' % args.target)
    sys.exit(0)
build_log = LOGS / ('mesa-tu-%s-build.log' % args.target)
with build_log.open('w') as stream:
    result = subprocess.run(['ninja', '-C', str(OUT), '-j6'], env=env, stdout=stream, stderr=subprocess.STDOUT)
if result.returncode:
    sys.exit('Build failed; see ' + str(build_log) + '\n' + '\n'.join(
        l for l in build_log.read_text().splitlines() if ': error:' in l or 'fatal error:' in l or l.startswith('FAILED:'))[:3000])
library = OUT / 'src/freedreno/vulkan/libvulkan_freedreno.dylib'
symbols = subprocess.run(['nm', '-gU', str(library)], capture_output=True, text=True).stdout
if ' T _vk_icdGetInstanceProcAddr' not in symbols:
    sys.exit('The library does not export vk_icdGetInstanceProcAddr')
print('PASS: Turnip with the darwin kernel backend builds for %s (%d bytes); no GPU or IOKit service was exercised'
      % (args.target, library.stat().st_size))
