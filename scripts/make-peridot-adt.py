#!/usr/bin/env python3
"""Generate the Apple-format device tree of the peridot board for UniXNU.

The board is the Xiaomi Poco F6 / Redmi Turbo 3 ("peridot", SM8635, a.k.a.
Qualcomm cliffs).  The hardware values below are taken from the device tree
that the board itself ships (Resources/DTBs/peridot.dts of the Mu-Silicium
tree) and from the measurements of the running device:

  - GICv3 distributor 0x17100000/0x10000, redistributor 0x17180000/0x200000,
    redistributor stride 0x40000, one redistributor region
    (interrupt-controller@17100000 of the board DT)
  - CPU timebase 19200000 Hz (timer clock-frequency 0x124f800)
  - eight cores, MPIDR affinity 0x000..0x700: three Cortex-A520
    (0x000-0x200), four Cortex-A720 (0x300-0x600), one Cortex-X4 (0x700)
  - UFS host 0x1d84000/0x3000, UFS PHY 0x1d80000/0x2000 (ufshc@1d84000)
  - the /arm-io window covers the APSS block that holds the GIC and the UFS
    host, so both can be children of the bus

The identity of the tree is the iPhone X (iPhone10,3 / D22AP): that is the
device whose iOS userland runs here.  The root identity strings and the
/product, /buttons, /defaults and /options properties are the ones of the real
D22AP device tree, extracted by scripts/extract-d22ap-identity.py.  The board
strings are appended to the root "compatible" property so that the board can
still be told apart from the original device.

The tree follows the contract of the generic ArmDTPlatform: /chosen with a
CHRP NVRAM proxy, /cpus, /arm-io, /defaults and /options are present, and
the memory map holds a placeholder for every sidecar the loader fills.
"""
from pathlib import Path
import argparse
import os
import struct
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d22ap_identity  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# The DRAM of the board, as the kernel needs it: gDramBase and gDramSize of
# XNU come from /chosen/dram-base and /chosen/dram-size, while the memory the
# kernel manages (gPhysBase/gPhysSize) comes from the loader window in the
# boot arguments.  The DRAM of peridot is fragmented: the low bank starts at
# 0x80000000 and the high banks are at 0x880000000 and 0x980000000.  The
# range below covers every bank the board device tree lists.
DRAM_BASE = 0x80000000
DRAM_SIZE = 0x380000000

# The /arm-io bus window.  It starts at the base of the SoC address space
# that the board DT uses and reaches to the end of the 4 GiB window, so that
# the GIC (0x17100000) and the UFS host (0x01d84000) are both inside it and
# can be children of the bus with offsets relative to the window.
ARMIO_BASE = 0x01000000
ARMIO_SIZE = 0x100000000 - ARMIO_BASE

GIC_DIST = 0x17100000
GIC_DIST_SIZE = 0x10000
GIC_REDIST = 0x17180000
GIC_REDIST_SIZE = 0x200000
GIC_REDIST_STRIDE = 0x40000

TIMEBASE = 19200000

UFS_HC = 0x01d84000
UFS_HC_SIZE = 0x3000
UFS_PHY = 0x01d80000
UFS_PHY_SIZE = 0x2000

# The board strings of the root "compatible" property.  The first entries of
# the property stay the ones of the target device: hw.model and hw.target are
# read from the root of the tree.
BOARD_COMPATIBLE = b'xiaomi,peridot\0qcom,sm8635\0'

# The core types of the SM8635: the affinity value selects the cluster.
CPU_TYPES = (
    (0x000, 0x300, b'arm,cortex-a520\0'),
    (0x300, 0x700, b'arm,cortex-a720\0'),
    (0x700, 0x800, b'arm,cortex-x4\0'),
)

# The identity seed of the platform.  It is a software seed, not an Apple
# silicon id: the board has no ECID, and the value only has to be stable and
# unique for this board so that IOPlatformUUID is published.
DEFAULT_UNIQUE_CHIP_ID = 0x50455249444F5401   # 'PERIDOT' + 1
DEFAULT_CHIP_ID = 0x8015                       # the chip id of the target device


def node(name, properties=(), children=()):
    properties = [('name', name.encode() + b'\0'), *properties]
    result = struct.pack('<II', len(properties), len(children))
    for key, data in properties:
        result += struct.pack('<32sI', key.encode(), len(data))
        result += data + bytes(-len(data) % 4)
    return result + b''.join(children)


def empty_nvram_proxy():
    """A fresh volatile CHRP bank for upstream IODTNVRAM, with no controller."""
    def header(name, size):
        raw = bytearray(struct.pack('<BBH12s', 0x70, 0, size // 16, name))
        checksum = sum(raw)
        while checksum > 255:
            checksum = (checksum & 255) + (checksum >> 8)
        raw[1] = checksum
        return raw

    image = bytearray(8192)
    image[:16] = header(b'nvram', 32)
    image[32:48] = header(b'common', 16 + 2048)
    free_at = 32 + 16 + 2048
    image[free_at:free_at + 16] = header(b'free', len(image) - free_at)
    struct.pack_into('<I', image, 16, zlib.adler32(image[20:]))
    return [('nvram-bank-size', struct.pack('<I', len(image))),
            ('nvram-current-bank', struct.pack('<I', 0)),
            ('nvram-bank-count', struct.pack('<I', 1)),
            ('nvram-proxy-data', bytes(image))]


def cpu_compatible(reg):
    for low, high, name in CPU_TYPES:
        if low <= reg < high:
            return name
    return b'arm,armv8\0'


def cpu_nodes(cpu_regs):
    nodes = []
    for index, reg in enumerate(cpu_regs):
        nodes.append(node('cpu%d' % index, [
            ('state', b'running\0' if index == 0 else b'waiting\0'),
            ('reg', struct.pack('<I', reg)),
            ('device_type', b'cpu\0'),
            ('compatible', cpu_compatible(reg)),
            ('timebase-frequency', struct.pack('<I', TIMEBASE)),
            # The logical id of the core and the cluster it belongs to.  One
            # homogeneous cluster: the board DT numbers the cores by affinity
            # only, and the topology follows the affinity value.
            ('cpu-id', struct.pack('<I', index)),
            ('cluster-id', struct.pack('<I', 0)),
            ('cluster-type', struct.pack('<I', 0)),
            ('die-cluster-id', struct.pack('<I', 0)),
            ('cluster-core-id', struct.pack('<I', index)),
            ('l2-cache-id', struct.pack('<I', index)),
            ('l3-cache-id', struct.pack('<I', 0)),
        ]))
    return nodes


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'build/peridot/boot/kernel.macho.adt')
    parser.add_argument('--dram-size', type=lambda value: int(value, 0), default=DRAM_SIZE,
                        help='Size of the memory window the kernel manages')
    parser.add_argument('--dram-base', type=lambda value: int(value, 0), default=DRAM_BASE,
                        help='Base of the memory window the kernel manages')
    parser.add_argument('--owned-memory-size', type=lambda value: int(value, 0), default=None,
                        help='Explicit DarwinBoot contiguous window request, 256 MiB..8 GiB in 2 MiB steps')
    parser.add_argument('--root-match-volume-uuid', default=None,
                        help='/chosen/root-matching: select the root by the UUID of an IOMedia (the standard source mechanism)')
    parser.add_argument('--unique-chip-id', type=lambda value: int(value, 16), default=DEFAULT_UNIQUE_CHIP_ID,
                        help='/chosen/unique-chip-id (8 bytes) and --chip-id (4 bytes) seed XNU IOPlatformUUID')
    parser.add_argument('--chip-id', type=lambda value: int(value, 16), default=DEFAULT_CHIP_ID)
    parser.add_argument('--cpu-regs', default='0,0x100,0x200,0x300,0x400,0x500,0x600,0x700',
                        help='Comma-separated CPU MPIDR affinity values (the /cpus reg of each core); the first is the running boot CPU')
    parser.add_argument('--psci-method', choices=['smc', 'hvc'], default='smc',
                        help='/psci method used by the secondary-CPU start (the board DT declares psci over smc)')
    parser.add_argument('--packed-data-ramdisk', action='store_true',
                        help='Hand off validated DBRDISK1 bytes to the native sparse block driver, without a dense memdev alias')
    parser.add_argument('--data-ramdisk', action='store_true',
                        help='/chosen/memory-map RAMDisk placeholder; the loader fills in the real range for a scratch Data seed')
    parser.add_argument('--persistent-data', action='store_true',
                        help='The Data disk keeps its writes across boots: no ephemeral-storage, so first-boot data migration runs')
    parser.add_argument('--trust-cache', action='store_true', help='Zeroed TrustCache sidecar handoff placeholder')
    parser.add_argument('--gpu-addon', action='store_true', help='Zeroed GpuAddon sidecar handoff placeholder')
    parser.add_argument('--text-fixup', action='append', default=[],
                        help='/chosen/text-fixups entry <file name>,<file offset>,<original>,<replacement> for the kernel\'s signed-text fixups')
    args = parser.parse_args()

    if not 0 < args.unique_chip_id < 1 << 64 or not 0 < args.chip_id < 1 << 32:
        parser.error('the identity seed must fit 8 bytes and the chip id 4 bytes, both nonzero')
    if args.owned_memory_size is not None and (
            not 0x10000000 <= args.owned_memory_size <= 0x200000000
            or args.owned_memory_size % 0x200000):
        parser.error('Owned memory must be 256 MiB to 8 GiB, aligned to 2 MiB')
    try:
        cpu_regs = [int(value, 0) for value in args.cpu_regs.split(',')]
    except ValueError:
        parser.error('--cpu-regs must be integers')
    if (not cpu_regs or cpu_regs[0] != 0 or len(set(cpu_regs)) != len(cpu_regs) or len(cpu_regs) > 8
            or any(reg < 0 or reg > 0xffff or reg & 0xff for reg in cpu_regs)):
        parser.error('--cpu-regs: up to eight distinct Affinity1-numbered cores, boot CPU 0 first')

    identity = d22ap_identity.IDENTITY
    product = node('product', [(key, value) for key, value in sorted(d22ap_identity.PRODUCT.items())])
    buttons = node('buttons', [(key, value) for key, value in sorted(d22ap_identity.BUTTONS.items())])
    # The platform defaults of the board, not the ones of the original device:
    # there is no SEP payload on this board and no suspend support, and the
    # vnode limit of the target kernel is not the one of this kernel.
    defaults = node('defaults', [('no-effaceable-storage', struct.pack('<I', 1)),
                                  ('sleep-disabled', struct.pack('<I', 1))])
    options = node('options', [])

    memory_map = node('memory-map', ([("PackedRAMDisk" if args.packed_data_ramdisk else "RAMDisk", bytes(16))]
                                      if (args.data_ramdisk or args.packed_data_ramdisk) else []) +
                                     ([('TrustCache', bytes(16))] if args.trust_cache else []) +
                                     ([('GpuAddon', bytes(16))] if args.gpu_addon else []))

    chosen = node('chosen', [
        ('random-seed', os.urandom(64)),
        ('unique-chip-id', struct.pack('<Q', args.unique_chip_id)),
        ('chip-id', struct.pack('<I', args.chip_id)),
        # The normal target OS.  The volatile Data RAM disk is described
        # separately by ephemeral-storage below.
        ('osenvironment', b'main\0'),
        # Security status as on a dev-fused, undemoted board (tuple 0,0,1,1),
        # as read by MobileGestalt: mobileactivationd takes its native
        # "Hactivation" branch (activated without an activation record; no
        # SEP and no baseband on this board).
        ('certificate-production-status', struct.pack('<I', 0)),
        ('effective-production-status-ap', struct.pack('<I', 0)),
        ('certificate-security-mode', struct.pack('<I', 1)),
        ('effective-security-mode-sep', struct.pack('<I', 1)),
        # This property describes the actual volatile Data RAM disk.  A
        # persistent one is not ephemeral: with the property datamigrator
        # skips every migration, so the staged system apps never install.
        *([('ephemeral-storage', struct.pack('<I', 1))]
          if (args.data_ramdisk or args.packed_data_ramdisk) and not args.persistent_data else []),
        *([('darwinboot-memory-size', struct.pack('<Q', args.owned_memory_size))]
          if args.owned_memory_size else []),
        ('dram-base', struct.pack('<Q', args.dram_base)),
        ('dram-size', struct.pack('<Q', args.dram_size)),
        # Image4 hash algorithm.  The target device tree specifies sha2-384 in
        # /chosen; this selects the algorithm only and asserts nothing about
        # Apple silicon or fuses.
        ('crypto-hash-method', b'sha2-384\0'),
        *([('root-matching', ('<dict><key>IOProviderClass</key><string>IOMedia</string>'
                               '<key>IOPropertyMatch</key><dict><key>UUID</key><string>' +
                               args.root_match_volume_uuid.upper() + '</string></dict></dict>\0').encode())]
          if args.root_match_volume_uuid else []),
        # Strict policy for the original AMFI: platform code only.  This keeps
        # AMFI enforcing; it does not relax it.
        ('amfi-only-platform-code', struct.pack('<I', 1)),
        *([('text-fixups', b''.join(f.encode() + b'\0' for f in args.text_fixup))] if args.text_fixup else []),
        *empty_nvram_proxy(),
    ], [memory_map,
        # Read by the original AppleImage4 at start-up; present and empty here.
        node('manifest-properties')])

    cpus = node('cpus', children=cpu_nodes(cpu_regs))
    psci = node('psci', [('compatible', b'arm,psci-1.0\0'), ('method', args.psci_method.encode() + b'\0')])

    arm_io = node('arm-io', [
        ('device_type', b'arm-io\0'),
        ('compatible', b'peridot-io\0arm-io\0'),
        ('#address-cells', struct.pack('<I', 2)),
        ('#size-cells', struct.pack('<I', 2)),
        ('ranges', struct.pack('<QQQ', 0, ARMIO_BASE, ARMIO_SIZE)),
    ], [
        node('intc', [('compatible', b'arm,gic-v3'),
                      ('interrupt-controller', b''),
                      ('reg', struct.pack('<4Q',
                                          GIC_DIST - ARMIO_BASE, GIC_DIST_SIZE,
                                          GIC_REDIST - ARMIO_BASE, GIC_REDIST_SIZE)),
                      ('redistributor-stride', struct.pack('<Q', GIC_REDIST_STRIDE)),
                      ('#redistributor-regions', struct.pack('<I', 1))]),
        # The UFS host that ABL leaves running, and its PHY.
        node('ufshc', [('compatible', b'qcom,ufshc\0'),
                       ('reg', struct.pack('<2Q', UFS_HC - ARMIO_BASE, UFS_HC_SIZE))]),
        node('ufsphy', [('compatible', b'qcom,ufs-phy-qmp-v4-cliffs\0'),
                        ('reg', struct.pack('<2Q', UFS_PHY - ARMIO_BASE, UFS_PHY_SIZE))]),
        # The panel of the board.  The geometry is the panel of the device
        # (1220x2712); the iPhone X userland works in 375x812 points.
        node('disp0', [('device_type', b'display-subsystem\0'),
                       ('compatible', b'peridot,display\0'),
                       ('canvas-width', struct.pack('<I', 1220)),
                       ('canvas-height', struct.pack('<I', 2712))]),
        # No PMU behind the watchdog of the board: the watchdog must not be
        # used to power the panel off.
        node('wdt', [('no-pmu', struct.pack('<I', 1))]),
    ])

    tree = node('device-tree', [
        # hw.model / hw.machine / hw.target come from the root identity
        # properties of the tree; libMobileGestalt prefix-matches hw.product
        # against iPhone/iPod/iPad, so the iPhone identity needs them here.
        ('model', identity['model']),
        ('target-type', identity['target-type']),
        ('target-sub-type', identity['target-sub-type']),
        ('manufacturer', identity['manufacturer']),
        ('compatible', identity['compatible'] + BOARD_COMPATIBLE),
        ('#address-cells', struct.pack('<I', 2)),
        ('#size-cells', struct.pack('<I', 2)),
    ], [chosen, defaults, options, cpus, psci, arm_io, buttons, product])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(tree)
    print(f'peridot ADT: {len(tree)} bytes, dram {args.dram_base:#x}+{args.dram_size:#x}, '
          f'{len(cpu_regs)} cores, timebase {TIMEBASE}')


if __name__ == '__main__':
    main()
