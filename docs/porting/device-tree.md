# Device tree

A device port deals with two trees:

| Tree | Format | Consumer |
| --- | --- | --- |
| UEFI device tree | Standard flattened device tree (FDT) | UEFI firmware, EFI and Linux entries |
| Apple device tree (ADT) | Apple node encoding | XNU platform expert and drivers |

The payload step generates the ADT as `kernel.macho.adt` next to the kernel. DarwinBoot reads it from the entry directory.

## Apple device tree encoding

An Apple device tree uses a compact node encoding:

```
u32 property_count
u32 child_count
for each property:
  char name[32]
  u32 length
  u8  value[length]
  padding to 4 bytes
for each child:
  node
```

Every node carries a `name` property with its own name and a terminating NUL.

The encoding is Apple's own. `dtc` compiles FDT sources, and libfdt functions read FDT blobs, so both apply to the UEFI tree only.

## Required nodes

The generic `ArmDTPlatform` requires these top level nodes:

| Node | Required contents |
| --- | --- |
| `/chosen` | `random-seed`, CHRP NVRAM proxy, DRAM description, `osenvironment` |
| `/cpus` | One `cpuN` child per core |
| `/arm-io` | Bus node with `#address-cells`, `#size-cells`, `ranges` |
| `/defaults` | Platform defaults |
| `/options` | Platform options |

The platform expert fails `configure()` when one of these nodes is absent. It also fails when `/chosen` has no usable NVRAM proxy.

### NVRAM proxy

XNU publishes the real `IODTNVRAM` from `/chosen`. The proxy uses the CHRP bank format:

| Property | Contents |
| --- | --- |
| `nvram-bank-size` | Bank size, 32-bit |
| `nvram-bank-count` | Number of banks, 32-bit |
| `nvram-current-bank` | Current bank index, 32-bit |
| `nvram-proxy-data` | The bank image |

The bank image contains a `nvram` header, a `common` header with a two kilobyte data area, and a `free` header. The `common` data area has an Adler-32 checksum at offset 16.

An empty proxy is enough for a device with no persistent NVRAM controller.

### Chosen properties

| Property | Type | Purpose |
| --- | --- | --- |
| `random-seed` | 64 bytes | Kernel entropy seed |
| `unique-chip-id` | 64-bit | Seeds `IOPlatformUUID` with `chip-id` |
| `chip-id` | 32-bit | Platform identity seed |
| `osenvironment` | string | `main`, `recoveryos` or `ramdisk` |
| `dram-base` | 64-bit | Physical DRAM base |
| `dram-size` | 64-bit | Physical DRAM size |
| `crypto-hash-method` | string | Image4 hash method, for example `sha2-384` |
| `root-matching` | dictionary | Root volume match dictionary |
| `ephemeral-storage` | 32-bit | Marks the writable Data volume as ephemeral |
| `darwinboot-memory-size` | 64-bit | Contiguous window request, 256 MiB to 8 GiB in 2 MiB steps |
| `amfi-only-platform-code` | 32-bit | Keeps AMFI in its platform code policy |
| `boot-manifest-hash` | bytes | Boot manifest hash for the owner path |

`unique-chip-id` and `chip-id` seed `IOPlatformUUID`. Without them, callers that pass a zero timeout to `gethostuuid()` wait indefinitely.

### Memory map

`/chosen/memory-map` holds the placeholders DarwinBoot fills:

| Property | Length | Filled with |
| --- | --- | --- |
| `RAMDisk` | 16 bytes | Address and size of the dense Data image |
| `PackedRAMDisk` | 16 bytes | Address and size of the packed Data image |
| `TrustCache` | 16 bytes | Address and size of the trust cache |

A placeholder is required for every input. A missing placeholder makes DarwinBoot return `EFI_COMPROMISED_DATA`.

### CPUs

```c
cpu0 {
  name = "cpu0";
  state = "running";
  reg = <0>;
  device_type = "cpu";
  compatible = "arm,cortex-a715";
  timebase-frequency = <19200000>;
}
```

The first CPU is the boot CPU. Its `reg` value is the MPIDR affinity value. More than one CPU adds a `/psci` node with `compatible = "arm,psci-1.0"` and `method = "smc"` or `"hvc"`.

### arm-io

```c
arm-io {
  name = "arm-io";
  device_type = "arm-io";
  #address-cells = <2>;
  #size-cells = <2>;
  ranges = <0 0x17000000 0x08000000>;
  intc {
    name = "intc";
    compatible = "arm,gic-v3";
    reg = <...>;
  };
}
```

`ranges` maps the bus window. Child `reg` values use offsets inside that window. A device below the window base cannot be expressed as a child; the driver then takes its physical addresses from board constants.

### product and buttons

`/product` supplies the product name and model. `/buttons` supplies the button names and `home-button-type`. MobileGestalt and the platform code read these nodes. The full property set, gesture setup and device family switch are in [MobileGestalt identity](/guide/mobilegestalt).

### Platform defaults

`/defaults` supplies platform options. For example, `sleep-disabled = <1>` prevents the CPU from parking when suspend is not implemented.

## ADT tool contract

`[payload.adt] tool` names a script in the device repository. The payload step calls it with the options listed in [Payload](/concepts/payload).

The tool writes the tree to `Payloads/kernel.macho.adt`. It must:

1. Generate valid Apple node encoding.
2. Add `random-seed` with a fresh 64-byte value.
3. Add the memory map placeholders for the inputs.
4. Add `unique-chip-id` and `chip-id` when a seed is supplied.
5. Add `root-matching` when a UUID is supplied.
6. Add `ephemeral-storage` for a Data seed.
7. Add `darwinboot-memory-size` when the window override is supplied.

## UEFI device tree

The firmware exposes its own FDT through `EFI_DTB_TABLE`. UniXNU can patch it and pass it to EFI or Linux entries.

An entry selects a tree:

```toml
[[entry]]
id = "linux"
type = "linux"
path = "Payloads/Image"
dtb = "DeviceTree/board.dtb"
```

`dtb = "firmware"` uses the firmware tree. A path uses a file on the payload volume. The tree is copied with 64 KiB of slack, global patches are applied, then entry patches, then `[entry.chosen]`.

Patches support `set`, `delete-prop`, `add-node`, `delete-node` and `overlay`:

```toml
[[dt_patch]]
op = "set"
node = "/chosen"
prop = "bootargs"
value = "console=ttyAMA0"

[[dt_patch]]
op = "overlay"
file = "DeviceTree/board.dtbo"
```

DarwinBoot reads the `.adt` sidecar. An `xnu` entry that sets `dtb` passes a tree in the loader request, and the shipped DarwinBoot refuses a request with a non-null device tree.

## Boot image device tree

The boot image carries a device tree after the gzip stream. The stock bootloader may require nodes that the firmware tree does not have.

```toml
[[bootimg.dtb_node]]
path = "/reserved-memory/splash_region"
props = [
  { name = "label", type = "s", value = "cont_splash_region" },
  { name = "reg", type = "x", value = ["0x0", "0xb8000000", "0x0", "0x2b00000"] },
]
```

`unixnu bootimg` applies these nodes with `fdtput` and verifies integer properties round-trip.

## Reference generators

| Generator | Purpose |
| --- | --- |
| `scripts/qemu-entry/make-dt.py` | QEMU fixture with a single CPU and optional GICv3, VirtIO and NVRAM |
| A device repository `make-<device>-adt.py` | Device tree with board addresses and identity |

The QEMU generator is the smallest complete example. The device page in [Devices](/devices/) records the values for a real board.

## Next steps

- [Payload](/concepts/payload)
- [Device tree matching](/drivers/device-tree-matching)
- [Bring-up order](/porting/bring-up)
