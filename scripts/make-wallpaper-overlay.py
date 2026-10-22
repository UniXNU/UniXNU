#!/usr/bin/env python3
"""Build the overlay for the default iPadOS 17 wallpaper's layered animation with PNG images in place of its HEIC ones.

  make-wallpaper-overlay.py SYSTEM_ROOT OUTPUT_DIR

SYSTEM_ROOT is the mounted OS volume of the IPSW (ipsw mount fs). The iPad7,1 variant of wallpaper 7570 (Flat, two image layers) is the
one PosterBoard picks on this device; its images are HEIC, which ImageIO cannot decode without a hardware HEVC decoder. OUTPUT_DIR gets
the animation's index.xml, assetManifest.caml and a main.caml that points at J120.png and J120-Dark.png next to it (converted with sips,
so this runs on macOS, and scaled to EDGE pixels). make-gpu-addon.py --wallpaper OUTPUT_DIR carries it to the kernel, which mounts it over the sealed animation."""
import subprocess
import sys
from pathlib import Path

ANIMATION = ('Library/Wallpaper/Collections/iPadOS_17~ipad.wallpaperCollection/Wallpapers/7570.iPadOS_17_Flat-1024w-1366h@2x~ipad.wallpaper/'
             '7570.iPadOS_17_Flat_Background-1024w-1366h@2x~ipad.ca')
IMAGES = ('J120', 'J120-Dark')
# The HEIC images are 3416 pixels square; PNG at that size does not fit the boot payload. The layers stretch their contents to their bounds.
EDGE = 2732


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    source, output = Path(sys.argv[1]) / ANIMATION, Path(sys.argv[2])
    if not (source / 'main.caml').is_file():
        sys.exit('No wallpaper animation at ' + str(source))
    if output.exists():
        sys.exit('Refuse to overwrite ' + str(output))
    output.mkdir(parents=True)
    for name in ('index.xml', 'assetManifest.caml'):
        (output / name).write_bytes((source / name).read_bytes())
    main_caml = (source / 'main.caml').read_text()
    for image in IMAGES:
        main_caml = main_caml.replace(f'"/assets/{image}.HEIC"', f'"/{image}.png"').replace(f'"assets/{image}.HEIC"', f'"{image}.png"')
        subprocess.run(['sips', '-Z', str(EDGE), '-s', 'format', 'png', str(source / 'assets' / f'{image}.HEIC'), '--out', str(output / f'{image}.png')],
                       check=True, stdout=subprocess.DEVNULL)
    if '.HEIC"/>' in main_caml:
        sys.exit('main.caml still points at a HEIC image')
    (output / 'main.caml').write_text(main_caml)
    for path in sorted(output.iterdir()):
        print(f'{path.stat().st_size:>10} {path.name}')


if __name__ == '__main__':
    main()
