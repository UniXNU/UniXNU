#!/usr/bin/env python3
"""Build the Vulkan loader and validation layer for arm64e macOS GPU diagnostics."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'Vulkan-Headers': '6802bb4733b63ed5efd3adb308a6c885ef180ea1',
    'Vulkan-Loader': 'fa218055ff4948b159f31d43f800c808a13d51df',
    'Vulkan-ValidationLayers': '15c64e73db67e27ff0215708fbe48684a35c6827',
}


def run(*command, **kwargs):
    subprocess.run([str(value) for value in command], check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=ROOT / '.cache/gpu-validation')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/gpu-validation-deps')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    sources, out = args.sources.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for name, pin in PINS.items():
        path = sources / name
        if not path.exists():
            path.mkdir(parents=True)
            run('git', 'init', '-q', path)
            run('git', '-C', path, 'fetch', '--depth=1', f'https://github.com/KhronosGroup/{name}.git', pin)
            run('git', '-C', path, 'checkout', '--detach', 'FETCH_HEAD')
        actual = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != pin:
            raise SystemExit(f'{path}: checkout differs from the pinned source')
    toolchain = out / 'arm64e.cmake'
    sdk = subprocess.check_output(['xcrun', '--sdk', 'macosx', '--show-sdk-path'], text=True).strip()
    toolchain.write_text(f'''set(CMAKE_OSX_ARCHITECTURES arm64e CACHE STRING "")
set(CMAKE_OSX_DEPLOYMENT_TARGET 27.0 CACHE STRING "")
set(CMAKE_OSX_SYSROOT "{sdk}" CACHE PATH "")
''')
    prefix = out / 'install'

    def build(name, *options):
        directory = out / name
        run('cmake', '-G', 'Ninja', '-S', sources / name, '-B', directory,
            '-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_TOOLCHAIN_FILE={toolchain}',
            f'-DCMAKE_INSTALL_PREFIX={prefix}', '-DBUILD_TESTS=OFF', *options)
        run('cmake', '--build', directory, '--parallel', args.jobs)
        run('cmake', '--install', directory)

    build('Vulkan-Headers', '-DUPDATE_DEPS=OFF')
    build('Vulkan-Loader', '-DUPDATE_DEPS=OFF', f'-DVULKAN_HEADERS_INSTALL_DIR={prefix}')
    build('Vulkan-ValidationLayers', '-DUPDATE_DEPS=ON', '-DUPDATE_DEPS_SKIP_EXISTING_INSTALL=ON',
          f'-DVULKAN_HEADERS_INSTALL_DIR={prefix}')
    package = out / 'files'
    library = package / 'lib'
    metadata = package / 'etc/vulkan/explicit_layer.d'
    library.mkdir(parents=True, exist_ok=True)
    metadata.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in ('libvulkan.1.dylib', 'libVkLayer_khronos_validation.dylib'):
        matches = list(prefix.rglob(name))
        if len(matches) != 1:
            raise SystemExit(f'expected one installed {name}, found {len(matches)}')
        target = library / name
        shutil.copyfile(matches[0], target)
        run('install_name_tool', '-id', '@rpath/' + name, target)
        run('codesign', '--force', '--sign', '-', '--pagesize', '4096', target)
        run('codesign', '--verify', '--strict', target)
        run('lipo', '-verify_arch', 'arm64e', target)
        copied.append(name)
    layer = next(prefix.rglob('VkLayer_khronos_validation.json'))
    data = json.loads(layer.read_text())
    data['layer']['library_path'] = '../../../lib/libVkLayer_khronos_validation.dylib'
    (metadata / layer.name).write_text(json.dumps(data, indent=2) + '\n')
    license_dir = package / 'licenses'
    license_dir.mkdir(exist_ok=True)
    repositories = [sources / name for name in PINS]
    external = sources / 'Vulkan-ValidationLayers/external/Release/64'
    repositories += [path for path in external.iterdir() if (path / '.git').exists()]
    for repository in repositories:
        for path in [*repository.glob('LICENSE*'), *repository.glob('NOTICE*')]:
            if path.is_file():
                shutil.copyfile(path, license_dir / (repository.name + '-' + path.name))
    (out / 'report.json').write_text(json.dumps(dict(sources=PINS, architecture='arm64e',
                                                   deployment='27.0', libraries=copied), indent=2) + '\n')
    print(f'GPU diagnostic dependencies: {package}')


if __name__ == '__main__':
    main()
