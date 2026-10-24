# Device tree matching

A driver binds to a provider through an IOKit personality. The personality is a dictionary of match keys.

## Procedure {#procedure}

1. Find the driver's [provider class](#provider-classes) and personality in the source. Record `IOClass`, `IOProviderClass` and matching keys.
2. Compare the personality with the generated [device-tree node](#device-tree-nodes). Check name, compatible values and property types using [examples](#matching-examples).
3. Update the owning personality or DTS/profile property. Check the [property reader](#reading-properties) so register widths and reference encoding match its expectations.
4. Rebuild the kernel for personality changes, and rebuild payload plus boot image for ADT changes. Inspect [probe order](#probe-order) and driver start logs to confirm the intended provider binds.

## Personality keys

| Key | Meaning |
| --- | --- |
| `IOClass` | Driver class |
| `IOProviderClass` | Provider class |
| `IONameMatch` | Provider name or `compatible` value |
| `IOPropertyMatch` | Dictionary of exact provider property values |
| `IOProbeScore` | Higher scores probe first |
| `IOMatchCategory` | Match category, which allows a second driver on the same provider |
| `IOResourceMatch` | Resource that must be published before probing |
| `IOProviderMergeProperties` | Properties added to the provider |

A personality without `IONameMatch` or `IOPropertyMatch` matches every provider of the named class. `IOProbeScore` decides which candidate wins.

## Provider classes

| Provider | Published by | Use |
| --- | --- | --- |
| `IOPlatformExpertDevice` | Platform expert | Platform identity, product and buttons |
| `IOPlatformDevice` | `ArmDTPlatform` for every `arm-io` child | SoC devices |
| `IOResources` | IOKit | Global resources such as AES or RAM block |
| `IOMedia` | Partition and file system stack | Root volume matching |
| `IOBlockStorageDevice` | Storage driver | Block device clients |

`ArmDTPlatform` attaches a nub to the platform expert for each `arm-io` child. The nub keeps the device tree parent, so `reg` and `ranges` resolve through `arm-io`.

## Matching examples

### Platform device by compatible

```c
"   ,{"
"     'IOClass'         = NativeUfs;"
"     'IOProviderClass' = IOPlatformDevice;"
"     'IONameMatch'     = 'qcom,sm8550-ufshc';"
"     'IOProbeScore'    = 1000:32;"
"   }"
```

`IONameMatch` compares against the provider name and the `compatible` string list.

### Global resource

```c
"   ,{"
"     'IOClass'         = NativeAES;"
"     'IOProviderClass' = IOResources;"
"     'IOResourceMatch' = IOBSD;"
"     'IOProbeScore'    = 1000:32;"
"   }"
```

`IOResourceMatch = IOBSD` waits until the BSD subsystem publishes its resource.

### Root volume by UUID

```xml
<key>IOProviderClass</key><string>IOMedia</string>
<key>IOPropertyMatch</key>
<dict>
  <key>UUID</key><string>00000000-0000-0000-0000-000000000000</string>
</dict>
```

This dictionary is stored in `/chosen/root-matching`.

## Device tree nodes

For format 2, edit the hardware DTS described in [Device tree](/porting/device-tree).
The SoC DTSI declares controller resources. A board using the SM8550 UFS host
enables its existing node:

```text
&ufs {
    status = "okay";
};
```

The included SoC node declares `reg = <0 0x1d84000 0 0x3000>` and
`unixnu,adt-name = "ufshc"`. Its parent uses two address cells, two size cells and
identity `ranges`. The converter exports the range to `/arm-io/ufshc` as a
little-endian u64 offset from the `arm-io` base followed by a u64 size. Configure clocks, power
and DMA in the consuming driver as required by [UFS adaptation](/porting/ufs).

## Reading properties

```cpp
OSData *data = OSDynamicCast(OSData, provider->getProperty("reg"));
if (data == nullptr || data->getLength() != 2 * sizeof(uint64_t)) {
  return false;
}
uint64_t range[2];
memcpy(range, data->getBytesNoCopy(), sizeof(range));
uint64_t physicalAddress = range[0];
uint64_t length = range[1];
```

This example consumes one format 2 ADT range on little-endian ARM64. A driver with multiple ranges validates and reads every address/size pair.

A string property:

```cpp
OSData *compatible = OSDynamicCast(OSData, provider->getProperty("compatible"));
if (compatible == nullptr || compatible->getLength() == 0) {
  return false;
}
const char *value = (const char *)compatible->getBytesNoCopy();
```

The string list is a sequence of NUL-terminated strings.

## Overlays and patches

A kit can apply a device tree overlay:

```toml
[[overlay]]
file = "board.dtbo"
```

A configuration can patch a property:

```toml
[[dt_patch]]
op = "set"
node = "/arm-io/intc"
prop = "status"
value = "disabled"
```

Patches apply to EFI and Linux entries. The Darwin path reads the `.adt` sidecar.

## Probe order

1. The platform expert publishes the provider.
2. IOKit collects personalities whose `IOProviderClass` matches.
3. Personalities whose `IONameMatch` or `IOPropertyMatch` fails are skipped.
4. `IOResourceMatch` providers must be published.
5. The remaining candidates are ordered by `IOProbeScore`.
6. Each candidate runs `probe()`.
7. The highest scoring candidate that starts owns the provider.

## Next steps

- [XNU drivers](/drivers/xnu-drivers)
- [Device tree](/porting/device-tree)
- [Kext bundles](/drivers/kexts)
