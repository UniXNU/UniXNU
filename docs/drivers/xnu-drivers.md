# XNU drivers

An XNU driver in UniXNU is a C++ IOKit class compiled into the kernel. The kernel links the driver as a static archive and starts it through a personality in `KernelConfigTables.cpp`.

## Source layout

```
drivers/MyDriver/
  MyDriver.cpp
  MyDriver.h
  Info.plist
```

`Info.plist` records the personality for reference. The kernel uses the personality compiled into `iokit/KernelConfigTables.cpp`.

## Driver class

```cpp
#include <IOKit/IOService.h>
#include <IOKit/IOLib.h>
#include <libkern/c++/OSData.h>

class MyDriver : public IOService {
  OSDeclareDefaultStructors(MyDriver)

public:
  bool start(IOService *provider) override;
  void stop(IOService *provider) override;
  bool probe(IOService *provider, SInt32 *score) override;
};

OSDefineMetaClassAndStructors(MyDriver, IOService)

bool MyDriver::probe(IOService *provider, SInt32 *score)
{
  if (!super::probe(provider, score)) {
    return false;
  }
  *score = 1000;
  return true;
}

bool MyDriver::start(IOService *provider)
{
  if (!super::start(provider)) {
    return false;
  }

  OSData *reg = OSDynamicCast(OSData, provider->getProperty("reg"));
  if (reg == nullptr || reg->getLength() != 4 * sizeof(uint32_t)) {
    IOLog("MyDriver: provider has no usable reg property\n");
    return false;
  }

  registerService();
  IOLog("MyDriver: started\n");
  return true;
}

void MyDriver::stop(IOService *provider)
{
  IOLog("MyDriver: stopped\n");
  super::stop(provider);
}
```

`start()` gets the provider, reads its properties, allocates resources, installs interrupt handlers and calls `registerService()`.

## Compile against the kernel ABI

The driver must use the same compiler flags as XNU. The kernel build records the exact command for every object in a `.cpo.json` file:

```
build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json
```

A build script reads that record, replaces the source path and the output path, adds the driver include paths, and runs the compiler:

```python
import json, subprocess
from pathlib import Path

record = json.loads(Path(
  "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json"
).read_text())

command = []
i = 0
while i < len(record["arguments"]):
  value = record["arguments"][i]
  if value == record["file"]:
    command.append("drivers/MyDriver/MyDriver.cpp")
  elif value == "-o":
    command += ["-o", "build/my-driver/MyDriver.o"]
    i += 1
  elif value == "-Xclang" and record["arguments"][i + 1].startswith("-W"):
    i += 1
  elif not value.startswith("-W"):
    command.append(value)
  i += 1

command += ["-Wall", "-Wextra", "-Werror", "-I", "build/my-driver"]
subprocess.run(command, cwd=record["directory"], check=True)
```

The resulting object must be:

| Field | Value |
| --- | --- |
| Magic | `0xfeedfacf` |
| CPU type | `0x0100000c` (ARM64) |
| File type | `1` (MH_OBJECT) |
| Subtype | `0` |
| Build version | platform `2` (iOS), minimum `0x110000` (17.0) |

The compile record carries the flags that make these values match the kernel.

## Archive

```sh
xcrun ar rcs build/my-driver/libMyDriver.a build/my-driver/MyDriver.o
```

Add the builder script to `[kernel] archives` in `board.toml`. `unixnu build kernel` runs it before the kernel link.

## Link into the kernel

Add the archive to `scripts/build-xnu-4k-baseline.sh`:

```sh
if [ "${XNU_MY_DRIVER:-0}" = 1 ]; then
  MY_DRIVER_ARCHIVE=$ROOT/build/my-driver/libMyDriver.a
  test -f "$MY_DRIVER_ARCHIVE"
  KERNEL_EXTRA_ARCHIVES="$KERNEL_EXTRA_ARCHIVES -Wl,-force_load,$MY_DRIVER_ARCHIVE"
  KERNEL_ARCHIVE_DEPENDENCIES="$KERNEL_ARCHIVE_DEPENDENCIES $MY_DRIVER_ARCHIVE"
fi
```

`-force_load` keeps every object, including classes the linker would otherwise drop. Add the archive to `KERNEL_ARCHIVE_DEPENDENCIES` so a changed archive relinks the kernel.

Enable it in the defconfig:

```
CONFIG_XNU_MY_DRIVER=y
```

## Add a personality

Add the match dictionary to `iokit/KernelConfigTables.cpp` through a patch:

```c
#if defined(XNU_MY_DRIVER) && XNU_MY_DRIVER
    "   ,{"
    "     'IOClass'         = MyDriver;"
    "     'IOProviderClass' = IOPlatformDevice;"
    "     'IONameMatch'     = 'my-device';"
    "     'IOProbeScore'    = 1000:32;"
    "   }"
#endif
```

The build script passes `-DXNU_MY_DRIVER=1` to `KernelConfigTables.cpo`:

```sh
EXTRA_MAKE_ARGS+=("KernelConfigTables.cpo_CFLAGS_ADD=-DXNU_MY_DRIVER=$MY_DRIVER")
```

The personality is a property list string in the kernel's IOKit configuration table. `IOClass` names the C++ class. `IOProviderClass` names the provider class. `IONameMatch` matches the provider name or a `compatible` value. `IOProbeScore` orders multiple candidates.

## Provider properties

The ADT node becomes an `IOPlatformDevice` nub when the platform expert matches it. Common properties:

| Property | Encoding | Use |
| --- | --- | --- |
| `reg` | 32-bit or 64-bit cells | Register window |
| `interrupts` | 32-bit cells | Interrupt numbers |
| `compatible` | string list | Driver match |
| `name` | string | Node name |
| `clock-frequency` | 32-bit | Input clock |
| `power-domains` | phandles | Power dependencies |

`provider->getProperty("reg")` returns an `OSData`. The number of address and size cells comes from the parent node.

## Memory

| API | Use |
| --- | --- |
| `IOMalloc`, `IOFree` | Kernel virtual memory |
| `IOMallocContiguous` | Physically contiguous memory |
| `IOBufferMemoryDescriptor` | DMA buffers with a physical address |
| `IODMACommand` | Map a buffer for a device |

A DMA buffer must be mapped through the device's IOMMU or SMMU context. The `ArmSmmu4K` kit provides 4 KiB SMMU tables.

## Interrupts

Use an interrupt event source from the provider or the platform:

```cpp
IOInterruptEventSource *source = IOInterruptEventSource::interruptEventSource(
  this, OSMemberFunctionCast(IOInterruptEventSource::Action,
  this, &MyDriver::handleInterrupt), provider, 0);

if (source == nullptr || !workLoop->addEventSource(source)) {
  return false;
}
source->enable();
```

The provider must publish an interrupt controller or an interrupt resource. `ArmCpu` supplies the GIC path on the generic ARM64 platform.

## Device tree resources

The platform expert publishes one nub per `arm-io` child. A driver that serves a device below the `arm-io` range takes its physical addresses from board constants.

A driver that matches `/product` or `/buttons` uses `IOPlatformExpertDevice` as the provider.

## Runtime behavior

| Stage | Call |
| --- | --- |
| Match | `probe()` |
| Start | `start()` |
| Publish | `registerService()` |
| Stop | `stop()` |

A driver that fails `start()` releases its resources and returns `false`.

## Testing

| Test | Method |
| --- | --- |
| Compile | `-Wall -Wextra -Werror` against the recorded flags |
| Object ABI | Check magic, CPU type, file type, subtype and build version |
| Host logic | Extract pure functions and compile a host test |
| Kernel boot | QEMU with the driver enabled and a boot progress log |
| Hardware | Boot the device and read the driver log |

## Reference drivers

| Driver | Demonstrates |
| --- | --- |
| `ArmDTPlatform` | Platform expert and device nubs |
| `ArmCpu` | CPU, GIC and timer |
| `NativeUfs` | Storage, SMMU and command queues |
| `NativeAES` | Accelerator subclass with original ABI |
| `NativeAdreno` | GPU power, GMU firmware, native 4 KiB SMMU, rings and user client |
| `NativeMetal` | Metal API frontend and metal2vulkan translation to Turnip |

The Adreno path is documented in [Adreno 740 driver](/drivers/native-adreno).

## Worked example

The [Novatek touch driver](/drivers/native-novatek-touch) shows the full structure: a pure processing core, a controller protocol behind a bus interface, board constants with sources, staged probing and HID publication.

## Next steps

- [Kext bundles](/drivers/kexts)
- [Device tree matching](/drivers/device-tree-matching)
- [Build the kernel](/guide/build-kernel)
