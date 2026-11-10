# Develop a driver

Write a driver when the [component catalog](/reference/components) has no
implementation for the hardware. Define its [boundary](/porting/drivers) first.
Run the build examples from the assembled target tree that `./unixnu tree` reports.

## 1. Choose the layer {#layer}

| Need | Layer | Built as | Loaded by |
| --- | --- | --- | --- |
| Display, input or storage before XNU | UEFI driver | EDK II `.efi` | Firmware dispatch, `[[driver]]` in `unixnu.toml`, or a kit |
| Platform, CPU, storage, display, GPU or any service inside XNU | Built-in XNU driver | Static archive linked into the kernel | The kernel at boot |
| A bundle that an external loader validates and injects | Kext bundle | `.kext` | A loader that accepts kext requests. The shipped DarwinBoot starts prelinked kernels |

## 2. Match the provider {#matching}

`ArmDTPlatform` publishes an `IOPlatformDevice` nub for every `arm-io` child of
the ADT. A driver binds through an IOKit personality:

| Key | Meaning |
| --- | --- |
| `IOClass` | Driver class |
| `IOProviderClass` | Provider class: `IOPlatformDevice` for SoC devices, `IOPlatformExpertDevice` for `/product` and `/buttons`, `IOResources` for global services |
| `IONameMatch` | Provider name or a `compatible` value |
| `IOPropertyMatch` | Exact provider property values |
| `IOResourceMatch` | Resource that must exist before probing, for example `IOBSD` |
| `IOProbeScore` | Higher scores probe first |
| `IOMatchCategory` | Lets a second driver match the same provider |

Built-in personalities are added to `iokit/KernelConfigTables.cpp` by a patch,
guarded by the driver's kernel flag:

```c
#if defined(XNU_MY_DRIVER) && XNU_MY_DRIVER
    "   ,{"
    "     'IOClass'         = MyDriver;"
    "     'IOProviderClass' = IOPlatformDevice;"
    "     'IONameMatch'     = 'vendor,my-device';"
    "     'IOProbeScore'    = 1000:32;"
    "   }"
#endif
```

The node's `compatible` and `unixnu,adt-name` come from the board DTS, see
[device tree](/porting/device-tree). A format 2 `reg` property is a sequence of
little-endian u64 address and size pairs.

## 3. Write the driver class {#driver-class}

```cpp
class MyDriver : public IOService {
  OSDeclareDefaultStructors(MyDriver)
public:
  IOService *probe(IOService *provider, SInt32 *score) override;
  bool start(IOService *provider) override;
  void stop(IOService *provider) override;
};
OSDefineMetaClassAndStructors(MyDriver, IOService)

bool MyDriver::start(IOService *provider)
{
  if (!IOService::start(provider)) return false;
  OSData *reg = OSDynamicCast(OSData, provider->getProperty("reg"));
  if (reg == nullptr || reg->getLength() != 2 * sizeof(uint64_t)) return false;
  registerService();
  return true;
}
```

`start()` reads the provider properties, maps registers, allocates DMA buffers
through the device's SMMU context, installs interrupt sources and calls
`registerService()`. A failed `start()` releases what it took and returns `false`.

## 4. Compile against the kernel ABI {#compile-against-the-kernel-abi}

The kernel build records the exact compiler command of every object in a
`.cpo.json` file, for example:

```
build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json
```

The driver recipe reads one record, replaces the source and output paths, adds
its include paths and runs the compiler. The object then has the architecture,
platform and deployment version of the selected kernel. A driver that
subclasses or calls a class of the original kernelcache also needs that
build's class layout, virtual method slots and symbol bindings, checked against
the kernelcache of the selected OS profile. Each OS profile has its own.

## 5. Link into the kernel {#link-into-the-kernel}

1. Archive the objects, for example `build/my-driver/libMyDriver.a`.
2. Put the recipe in the device repository's `scripts/` and add it to
   `[kernel] archives` in dependency order. Set `CONFIG_XNU_BUILD_ARCHIVES=y`.
3. Add the archive to the kernel link in the defconfig:

   ```
   CONFIG_XNU_EXTRA_LD_ARCHIVES="-Wl,-force_load,{tree}/build/my-driver/libMyDriver.a"
   ```

   `-force_load` keeps every object, including classes nothing references.
4. Enable the flag that guards the personality: `CONFIG_XNU_<NAME>=y` in the
   defconfig, read in `scripts/build-xnu-4k-baseline.sh` and passed to
   `KernelConfigTables.cpo` as `-DXNU_<NAME>=1`, see [Build the kernel](/guide/build-kernel).
   A board-started service is called from the board initialization instead.
5. Run `./unixnu build kernel` from the main checkout and inspect the archive
   log under `logs/` and the prelink report.

A reusable driver becomes a component: give it a repository and a
`components.toml` entry with `build`, `outputs`, dependencies and OS ABI, then
select it with `component:<ID>`.

## 6. Add a UEFI driver {#uefi-driver}

A UEFI driver is an EDK II module with an INF, listed in a DSC.

| Location | Build | Load |
| --- | --- | --- |
| Firmware volume | Add the INF to the firmware DSC and FDF, then run `./unixnu build firmware` | Firmware dispatch |
| Payload | Build a standalone `.efi` | `[[driver]]` in `unixnu.toml` or in a kit, see [boot configuration](/reference/boot-configuration) |

The driver receives the `args` of its `[[driver]]` entry as load options.
`connect = true` runs `ConnectController` on every handle after it starts.
Follow [firmware integration](/porting/uefi-firmware) for the DSC and FDF.

## 7. Verify {#verify}

| Check | Method |
| --- | --- |
| Compile | `-Wall -Wextra -Werror` on top of the recorded flags |
| Archive | `llvm-ar t` and `llvm-nm --defined-only` show the objects and the start symbol |
| Host logic | Compile the hardware-independent functions as a host test |
| Device | Boot and read the driver's start line with [log capture](/porting/log-capture) |

Record the result in the owning area of [porting.toml](/porting/records), then
return to the [adaptation sequence](/porting/drivers).
