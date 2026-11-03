# Adapt the drivers

Use this checklist after [creating and resolving the device repository](/porting/steps).
Start with platform services, then add one peripheral path at a time. Read the
linked guide before selecting that component or copying its board integration.

## 1. Define the driver boundary

Read the [component catalog](/reference/components) and the subsystem's source
map below. For each selected implementation, write down:

| Boundary | Required definition |
| --- | --- |
| Hardware | Register ranges, access widths, interrupts, clocks, reset and power owner |
| Transport | Request format, response matching, timeout, retry and disconnect handling |
| Memory | CPU/DMA addresses, buffer size/alignment, cache policy and release point |
| OS | Provider class, properties, ABI version, entry points and completion notifications |
| Build | Source files, dependencies, archive output, link input and initialization caller |

Use the target DTS, firmware and driver sources for hardware values. Record their
file and revision beside the configuration. Keep SoC operations in shared support,
board wiring/policy in the device repository and OS ABI bindings in the selected
OS integration. The device sources linked in these guides are implementation examples.

From the main checkout, resolve the target:

```sh
./unixnu status --json
./unixnu tree
```

Use the reported target tree for low-level build commands. Components are under
`drivers/` or `kits/`; the device package is linked at `kits/<board.kit>`.

## 2. Follow the hardware sequence

| Order | Capability | Adaptation guide | Implementation to inspect |
| --- | --- | --- | --- |
| 1 | CPU, interrupts, timer, RAM, DMA | [Platform and memory](/porting/platform) | ArmDTPlatform, ArmCpu, ArmSmmu4K, SoC DTSI |
| 2 | Storage, root, persistent Data | [UFS](/porting/ufs) and [block/root integration](/porting/platform#block-and-os-services) | ShengUfs, RamBlock, VirtioMmioBlock, VerifiedRoot |
| 3 | Framebuffer, refresh, brightness | [Display and brightness](/porting/display) | GopFramebuffer, DisplayTimingProbe, AppleARMBacklight, GeniI2c |
| 4 | Touch and physical buttons | [Input](/porting/input) | QcomGeniSpi, ShengNovatekTouch, ShengHidInput, ButtonProbe |
| 5 | GPU and Metal | [GPU](/porting/gpu) | Adreno740, AdrenoMetal, Sm8550Platform, AdrenoFirmware, AdrenoPM4, AirNir |
| 6 | Wi-Fi | [Network](/porting/network) | Ath12kWifi, WifiProbe, WifiNet, MhiBoot |
| 6a | Baseband and cellular, when fitted | [Baseband](/porting/baseband) | QcomBaseband, modem boot, QRTR, IPA/GSI |
| 7 | DSP, audio, battery, CPU frequency, platform power | [DSP and power](/porting/power) | AdspProbe, AudioProbe, ShengBattery, CpuFreqProbe, ShengPlatformPower |
| 8 | OS services and packaging | [OS integration](/porting/platform#block-and-os-services) and [firmware](/porting/uefi-firmware) | SoftwareAES, AppleKeyStoreState, XnuPrelink, DarwinBoot, ShengPreflight |

Each guide links the interfaces and reference implementations to inspect.
Implement controller, power and DMA operations for the target hardware, then
qualify private ABI bindings against the selected OS kernelcache.

## 3. Connect initialization, ABI and build inputs {#build-integration}

Read these working integration references:

| Source | What to trace |
| --- | --- |
| [board.toml](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/board.toml) | Component selection and ordered archive commands |
| [build-gop-legacy-display.py](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/scripts/build-gop-legacy-display.py#L253) | Kernel compile-record reuse, source objects, ABI inputs and archive creation |
| [LegacyDisplayProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/LegacyDisplayProbe.cpp#L493) | `native_legacy_display_late_probe`: board initialization calls and dependency order |
| [BatteryProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/BatteryProbe.cpp#L16) | `OSMetaClass::preModLoad/postModLoad` around a late class initializer |
| [Built-in driver example](/drivers/xnu-drivers#driver-class) | `IOService` lifecycle, provider matching and archive/link setup |

1. **Choose the startup path.** A provider-matched service needs a personality,
   `probe/start` and the provider properties described in
   [matching](/drivers/device-tree-matching). A board-started service needs an
   explicit caller after its resources and OS dependencies exist. Keep class
   initialization consistent with the selected build's normal or late registration.
2. **Complete resource cleanup.** Pair each mapping, interrupt, work-loop source,
   timer, DMA buffer and service reference with its owner and release operation.
   Stop new requests, cancel/drain outstanding work, then release those resources
   on initialization failure, detach and reset.
3. **Compile for the selected OS.** Use that kernel's generated headers and compile
   records as described in [XNU drivers](/drivers/xnu-drivers#compile-against-the-kernel-abi).
   For private interfaces, record the class layout, virtual-method slots, selectors,
   argument structures and symbol bindings against the selected kernelcache.
   Supply the candidate/audit files required by the chosen recipe through
   [build inputs](/porting/migration#build-inputs).
4. **Add the recipe.** Put device build scripts under its `scripts/` and hardware
   sources under `package/`. Adapt the reference recipe's compile-record lookup,
   source list, include paths, class-initializer handling and archive destination.
   It must produce the archive named by the link configuration. For a reusable
   component, update the catalog's `build`, `outputs`, dependencies and OS ABI.
5. **Connect selection and linking.** Add the component ID to the complete
   `[components] include` list. Place `component:<ID>` or the device script command
   in `[kernel] archives` in dependency order. With archive builds, enable
   `CONFIG_XNU_BUILD_ARCHIVES=y`. Set the consumed driver flags/archive paths and
   [link inputs](/drivers/xnu-drivers#link-into-the-kernel). Trace a new flag through
   the build scripts and its initialization caller.
6. **Check the resolved inputs.** Run `./unixnu status --json` from the main checkout.
   Confirm source revisions, dependency order and the archive path. Run
   `./unixnu kernel`, then inspect its archive log and prelink output.
7. **Check the linked implementation.** In the reported target tree, use the tools
   installed with the selected LLVM toolchain:

   ```sh
   llvm-ar t <archive.a>
   llvm-nm --defined-only <archive.a>
   ```

   Find the expected driver objects and startup symbol, then confirm the kernel's
   prelink report includes the archive. Build `./unixnu payload` and
   `./unixnu bootimg` from the main checkout with the target's local inputs.
8. **Exercise one complete operation.** Follow the subsystem's checks: request,
   hardware completion, OS-visible result, then release or repeat. Capture the
   return code and the last completed stage with [logs](/porting/log-capture).

**Result:** the driver has a traceable startup path, resolves its selected OS ABI,
is linked into the kernel and completes the operation under test.

## 4. Record the result

For every capability, record the source revision, firmware, boot arguments,
command, artifact path, last successful stage and captured result in
`porting.toml`. Use the [completion levels](/porting/records#completion-levels)
for source review, host checks and device observations.

A missing input belongs in the record with the next action needed to obtain it.
The next device stage starts when its prerequisites are verified. Return to
[bring-up](/porting/bring-up) to integrate the completed paths.
