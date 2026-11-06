#!/usr/bin/env python3
"""Build the minimal Apple Device Tree that the SWEET xnu needs to boot.

Only what the early boot path actually reads (see NOTES.md); every MMIO
address comes from the sweet live FDT. Usage:  mkadt.py OUT.adt [--dump] [--qemu] [--highmem] [--board umi]
"""
import hashlib, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adt  # noqa: E402

# Kernel-managed RAM: above every Qualcomm XPU carve-out (see NOTES.md)
PHYS_BASE = 0xb0000000
MEM_SIZE = 0x4d000000
# --highmem (phone only): the whole upper DDR bank. The live FDT memory node is
# <0x80000000 2G>, <0x1_00000000 0xfcc00000>; every fixed reserved-memory
# carve-out is in the low bank and the dynamic pools are limited below 4G.
HIGH_PHYS_BASE = 0x100000000
HIGH_MEM_SIZE = 0xfcc00000
# umi (Mi 10, 8 GB): live FDT memory <0x80000000 0x3bb00000>, <0xc0000000 0xc0000000>, <0x1_80000000 4G>, so
# 0x1_00000000..0x2_80000000 is one 6 GiB stretch with no reserved-memory in it (/proc/iomem System RAM
# ffc20000-27fffffff; TWRP 2026-11-06). 0xc0000000..0xffc00000 stays unmanaged for the display/Wi-Fi/DSP pools.
UMI_HIGH_MEM_SIZE = 0x180000000
# (0253) and down into <0xc0000000 0xc0000000>: our fixed low-RAM pools (sweetfb 0xc0000000 x 6 x 16 MiB when direct,
# Wi-Fi 0xd0000000, WLFW 0xd1000000, SLPI/FastRPC 0xd3000000-0xd4d00000, PCM 0xd3800000) all end below 0xd5000000,
# so XNU takes 0xd6000000..0x2_80000000 (6.66 GiB). The 128 KiB at 0xffc00000 that Linux shows as not System RAM
# is a dynamic reserved-memory pool Linux allocated itself (no fixed reg there): plain RAM under iOS.
UMI_LOW_PHYS_BASE = 0xd6000000
# /arm-io children are relative to this; it must not be 0 (serial_init bails)
SOC_BASE = 0x01000000

GICD, GICD_SIZE = 0x17a00000, 0x10000
GICR, GICR_SIZE = 0x17a60000, 0x100000
FB, FB_SIZE = 0x9c000000, 0x1700000
SWEET_ECID = 0x5357454554000001  # 'SWEET' + 1, synthetic
FB_W, FB_H, FB_STRIDE = 1080, 2400, 1080 * 4
# Internal UFS host (ufshc@1d84000 "ufs_mem"); QEMU virt has none
UFS, UFS_SIZE = 0x01d84000, 0x3000
TIMEBASE = 19200000
VTIMER_INTID = 19
# QEMU virt (-M virt,gic-version=3 -cpu cortex-a76): GICD/GICR and the generic timer's CNTFRQ
QEMU_GICD, QEMU_GICR, QEMU_TIMEBASE = 0x08000000, 0x080a0000, 62500000
QEMU_VTIMER_INTID = 27

# Xiaomi Mi 10 (umi, SM8250), from its live FDT. GIC, UFS host, splash
# framebuffer base and the upper-bank RAM range above are the same as sweet;
# what differs: 1080x2340 panel, the standard timer PPIs (virtual timer =
# INTID 27, sweet uses 19), and 4 A55 + 3 A77 + 1 A77 prime cores.
BOARDS = {
    'sweet': dict(fb_h=2400, vtimer=VTIMER_INTID, cpu='qcom,kryo470', soc='qcom,sm7150',
                  clocks=[1804800000] * 6 + [2304000000] * 2),
    'umi': dict(fb_h=2340, vtimer=27, cpu='qcom,kryo585', soc='qcom,sm8250',
                clocks=[1804800000] * 4 + [2419200000] * 3 + [2841600000]),
}

BOOT_MANIFEST_HASH = hashlib.sha384(b'sweet boot manifest').digest()

# The iOS userland is the iPhone X (iPhone10,3 / D22AP) IPSW. MobileGestalt
# derives product type, device class, home-button-less UI, artwork etc. from
# the root identity and /product of the real D22AP device tree. That tree is
# an Apple artifact (kept out of git): extract it from the IPSW with
#   tools/remotezip.py URL DeviceTree.d22ap.im4p DIR
#   ipsw img4 im4p extract DIR/Firmware/all_flash/DeviceTree.d22ap.im4p -o d22ap.adt
D22AP_ADT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../research/ipsw-x/d22ap.adt')
GPU_FW_UMI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../research/gpu-fw/umi')


def d22ap_product(path=D22AP_ADT):
    """/product properties of the real D22AP tree, without the syscfg
    placeholders iBoot would fill in (flag bit set) and the node bookkeeping."""
    if not os.path.exists(path):
        print(f'warning: {path} missing, no /product node', file=sys.stderr)
        return None
    root, _ = adt.parse(open(path, 'rb').read())
    for c in root.children:
        if dict((k, v) for k, f, v in c.props).get('name') == b'product\0':
            return [(k, v) for k, f, v in c.props if not f and k not in ('name', 'AAPL,phandle')]
    raise SystemExit(f'{path}: no /product node')

u32 = lambda *v: struct.pack('<%dI' % len(v), *v)
u64 = lambda *v: struct.pack('<%dQ' % len(v), *v)
cstr = lambda s: s.encode() + b'\0'


def node(name, props=(), children=()):
    n = adt.Node()
    n.props = [('name', 0, cstr(name))] + [(k, 0, v) for k, v in props]
    n.children = list(children)
    return n


def build(seed=None, qemu=False, highmem=False, board='sweet'):
    """qemu=True: same tree, but with QEMU virt's GIC addresses and CNTFRQ (tools/qemu-sweet.py)."""
    phys_base, mem_size = (HIGH_PHYS_BASE, HIGH_MEM_SIZE) if highmem else (PHYS_BASE, MEM_SIZE)
    if highmem and board == 'umi' and not qemu:
        mem_size = UMI_HIGH_MEM_SIZE
        if os.environ.get('UMI_LOW_RAM') == '1':   # 6.66 GB from 0xd6000000: the persistent log stopped (NOTES)
            phys_base, mem_size = UMI_LOW_PHYS_BASE, HIGH_PHYS_BASE + UMI_HIGH_MEM_SIZE - UMI_LOW_PHYS_BASE
    gicd, gicr, timebase = (QEMU_GICD, QEMU_GICR, QEMU_TIMEBASE) if qemu else (GICD, GICR, TIMEBASE)
    b = BOARDS[board]
    seed = seed if seed is not None else os.urandom(64)
    phandle = iter(range(1, 1000))
    ph = lambda: ('AAPL,phandle', u32(next(phandle)))

    chosen = node('chosen', [
        ph(),
        ('dram-base', u64(phys_base)),
        ('dram-size', u64(mem_size)),
        ('random-seed', seed),
        ('debug-enabled', u32(1)),
        ('firmware-version', cstr(f'{board}-shim')),
        ('system-firmware-version', cstr(f'{board}-shim')),
        # iBoot's SHA-384 of the boot manifest; /sbin/mount -P 1 exits unless
        # it exists (bind mounts /private/preboot/<hex>/usr/standalone/firmware,
        # tolerating a missing directory). Fixed stand-in value.
        ('boot-manifest-hash', BOOT_MANIFEST_HASH),
        # libimg4 (cryptexd) aborts "failed to get crypto algorithm" without
        # it; real A11+ device trees say sha2-384.
        ('crypto-hash-method', cstr('sha2-384')),
        # MobileGestalt's screen class: display-scale (u32, default 0) comes
        # from /chosen, the pixel size from IOMobileFramebuffer. Scale 0 makes
        # SpringBoard's FBSDisplayMode "infxinf@0x" invalid. 1080x2400 @3x =
        # 360x800 points (like iPhone X class devices).
        ('display-scale', u32(3)),
        # XNU derives IOPlatformUUID (gethostuuid) from these on arm; without
        # them CFPreferences cannot use kCFPreferencesCurrentHost (no ByHost
        # files), so e.g. DataMigration never records LastSystemVersion and
        # migrates on every boot. Synthetic ECID (not the phone's); chip-id
        # of the A11 that the iPhone X userland expects.
        ('unique-chip-id', struct.pack('<Q', SWEET_ECID)),
        ('chip-id', u32(0x8015)),
        # Security status as on a dev-fused, undemoted board (tuple 0,0,1,1):
        # MobileGestalt reads these from /chosen, and mobileactivationd's
        # DeviceType then takes its native "Hactivation" branch (state
        # Activated without an activation record; no SEP, no baseband here).
        ('certificate-production-status', u32(0)),
        ('effective-production-status-ap', u32(0)),
        ('certificate-security-mode', u32(1)),
        ('effective-security-mode-sep', u32(1)),
    ] + ([
        # iBoot puts the radio MACs here. MobileGestalt's WifiAddress (needed
        # for the A11 UniqueDeviceID, which lsd asks for while seeding the
        # LaunchServices database) reads mac-address-wifi0 and otherwise
        # waits forever for an IONetworkController to match: with no Wi-Fi
        # and sweetusb=0 that blocks lsd and SpringBoard on the Apple logo.
        # Synthetic, locally administered addresses (not the phone's).
        ('mac-address-wifi0', bytes.fromhex('025357454501')),
        ('mac-address-bluetooth0', bytes.fromhex('025357454502')),
    ] if board == 'umi' else []), [node('memory-map', [ph()]),
        # Local boot policy (kern_csr.c): SIP relaxed like `csrutil disable`
        # (lp-sip0: untrusted kexts, unrestricted FS, task_for_pid, kernel
        # debugger, dtrace, nvram), lp-sip1: unauthenticated (unsealed) root.
        # The iOS shared cache is in no trust cache, so dyld can only map it
        # with CSR_ALLOW_UNRESTRICTED_FS (vm_unix.c shared region checks).
        node('asmb', [ph(), ('lp-sip0', u64(0x6f)), ('lp-sip1', u32(1))])])

    # SWEET SMP: all eight cores in physical-core order (0-5 Cortex-A55,
    # 6-7 Cortex-A76), one homogeneous cluster. The kernel defaults to one
    # and uses cpus=N to select an initial prefix (N <= 8).
    # QEMU retains its original single-CPU tree: its MPIDRs differ from sweet.
    cpu_nodes = []
    for core in range(1 if qemu else 8):
        cpu_nodes.append(node(f'cpu{core}', [
            ph(),
            ('device_type', cstr('cpu')),
            # SweetCPU matches IONameMatch 'qcom,kryo470' (xnu 0018): other
            # boards keep it as a second entry or no CPU driver attaches and
            # boot waits forever for gIOAllCPUInitializedKey.
            ('compatible', cstr(b['cpu']) + (cstr('qcom,kryo470') if b['cpu'] != 'qcom,kryo470' else b'') + cstr('ARM,v8')),
            ('reg', u32(core << 8)),  # actual MPIDR Aff1:Aff0, NOT logical ID
            ('cpu-id', u32(core)),   # descriptive: XNU assigns IDs by DT order
            ('cluster-id', u32(0)),  # descriptive; see ml_parse_cpu_topology
            ('cluster-type', u32(0)),  # homogeneous CLUSTER_TYPE_SMP, not AMP
            ('die-cluster-id', u32(0)),
            ('cluster-core-id', u32(core)),
            ('l2-cache-id', u32(core)),  # distinct per-core L2 nodes in live FDT
            ('l3-cache-id', u32(0)),     # shared L3
            ('state', cstr('running' if core == 0 else 'stopped')),
            ('timebase-frequency', u32(timebase)),
            ('clock-frequency', u32(b['clocks'][core])),
            ('bus-frequency', u32(100000000)),
            ('memory-frequency', u32(1866000000)),
            ('peripheral-frequency', u32(timebase)),
            ('fixed-frequency', u32(timebase)),
        ]))
    cpus = node('cpus', [ph(), ('#address-cells', u32(1)),
                         ('#size-cells', u32(0))], cpu_nodes)

    gic = node('gic', [
        ph(),
        ('compatible', cstr('arm,gic-v3')),
        ('interrupt-controller', b''),
        ('virtual-timer-intid', u32(QEMU_VTIMER_INTID if qemu else b['vtimer'])),
        ('reg', u64(gicd - SOC_BASE, GICD_SIZE, gicr - SOC_BASE, GICR_SIZE)),
    ])
    arm_io = node('arm-io', [
        ph(),
        ('device_type', cstr('sweet-io')),
        ('compatible', cstr('sweet-io') + cstr('arm-io')),
        ('#address-cells', u32(2)),
        ('#size-cells', u32(2)),
        ('ranges', u64(0, SOC_BASE, 0x100000000 - SOC_BASE)),
    ], [gic,
        # No hardware: watchdogd checks IODeviceTree:/arm-io/wdt for no-pmu and
        # otherwise crashes trying to set the PMU boot stage (customer builds
        # ignore the -wdt_no_pmu boot-arg).
        node('wdt', [ph(), ('no-pmu', u32(1))]),
        # Main display: IOMobileFramebuffer.framework counts /arm-io children
        # with this device_type and reads the canvas size from the node
        # (the presented iPhone X size, see SweetFramebuffer.cpp);
        # the kernel's AppleCLCD matches the compatible string.
        node('disp0', [
            ph(),
            ('device_type', cstr('display-subsystem')),
            ('compatible', cstr('sweet,display')),
            ('canvas-width', u32(1125)),
            ('canvas-height', u32(2436)),
        ])] + ([
        # umi Wi-Fi (QCA6390, kernel 0153+ en0): launchd starts wifid only when the
        # device tree has a "wlan" node (com.apple.wifid _LimitLoadToDeviceTree =
        # wlan, as the ios-topaz notes say); device_type as on D22AP's
        # /arm-io/uart4/wlan, MAC = /chosen mac-address-wifi0.
        node('wlan', [
            ph(),
            ('device_type', cstr('wlan')),
            ('compatible', cstr('wlan-pcie,qca6390') + cstr('wlan-pcie,qcom')),
            ('local-mac-address', bytes.fromhex('025357454501')),
        ])] if board == 'umi' else []))

    # umi GPU firmware (xnu bsd/dev/sweet_adreno.c reads it from here): the phone's own
    # /vendor/firmware/a650_* copied into research/gpu-fw/umi/ (Qualcomm's: never in git).
    # A node with no compatible, so nothing in iOS matches it.
    gpufw = []
    if board == 'umi' and os.path.isdir(GPU_FW_UMI):
        files = sorted(f for f in os.listdir(GPU_FW_UMI) if f.startswith('a650_'))
        if files:
            gpufw = [node('sweet-gpufw', [ph()] + [(f, open(os.path.join(GPU_FW_UMI, f), 'rb').read()) for f in files])]

    fbcon = node('sweet-fbcon', [
        ph(),
        ('reg', u64(FB, FB_SIZE)),
        ('width', u32(FB_W)),
        ('height', u32(b['fb_h'])),
        ('stride', u32(FB_STRIDE)),
    ])

    # bsd/dev/sweet_ufs.c: the UFS host ABL leaves running (absolute physical reg).
    ufs = node('sweet-ufs', [
        ph(),
        ('compatible', cstr('qcom,ufshc')),
        ('reg', u64(UFS, UFS_SIZE)),
    ])

    # pmap_compute_max_asids requires the node even when no overrides are set.
    # An absent pmap-max-asids property selects XNU's own MAX_ASIDS default.
    # No effaceable storage: keybagd then reads /private/var/keybags/systembag.kb
    # as a plain plist instead of decrypting it with the effaceable key.
    defaults = node('defaults', [ph(), ('no-effaceable-storage', u32(1))])

    # MobileGestalt HomeButtonType = IODeviceTree:/buttons home-button-type
    # (D22AP: 2, no Home button; absent = 0 = Home-button device).
    buttons = node('buttons', [
        ph(),
        ('button-names', cstr('volup') + cstr('voldown') + cstr('hold')),
        ('home-button-type', u32(2)),
        ('opposed-power-vol-buttons', u32(1)),
    ])

    product_props = d22ap_product()
    if product_props and board == 'umi':
        # Settings > General > About "Model Name" is MobileGestalt's marketing
        # name = /product product-name; ProductType stays iPhone10,3 (root model).
        names = {'product-name': cstr('Xiaomi Mi 10'), 'product-description': cstr('Xiaomi Mi 10')}
        product_props = [(k, names.get(k, v)) for k, v in product_props]
    product = [node('product', [ph()] + product_props)] if product_props else []

    # Identity of the iPhone X whose userland runs here: compatible[0] is
    # hw.model/hw.target (D22AP), model is hw.machine/hw.product
    # (iPhone10,3). 'xiaomi,sweet' stays for SweetPlatformExpert matching,
    # also on umi.
    return node('device-tree', [
        ph(),
        ('compatible', cstr('D22AP') + cstr('iPhone10,3') + cstr('xiaomi,sweet') + (cstr('xiaomi,umi') if board == 'umi' else b'') + cstr(b['soc']) + cstr('AppleARM')),
        ('model', cstr('iPhone10,3')),
        ('target-type', cstr('D22')),
        ('target-sub-type', cstr('D22AP')),
        ('manufacturer', cstr('Apple Inc.')),
        ('#address-cells', u32(2)),
        ('#size-cells', u32(2)),
    ], [chosen, defaults, cpus, arm_io, fbcon, buttons] + product + ([] if qemu else [ufs]) + gpufw)


if __name__ == '__main__':
    board = sys.argv[sys.argv.index('--board') + 1] if '--board' in sys.argv else 'sweet'
    root = build(qemu='--qemu' in sys.argv, highmem='--highmem' in sys.argv, board=board)
    blob = adt.serialize(root)
    open(sys.argv[1], 'wb').write(blob)
    if '--dump' in sys.argv:
        adt.dump(adt.parse(blob)[0])
    print(f'{sys.argv[1]}: {len(blob)} bytes', file=sys.stderr)
