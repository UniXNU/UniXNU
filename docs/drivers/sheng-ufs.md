# ShengUfs

Start with the [adaptation procedure](/porting/ufs) for board inputs, source changes, build integration and verification order.

ShengUfs provides the sheng UFS storage path for SM8550. It owns the host
controller, SMMU mappings, command queues, and root reads. Its board integration
includes clock resources and the persistent Data and log regions. On request it
also gives the display bank (`sheng-dpu-scanout`) and the WiFi endpoint
(`sheng-wifi=2` or more) stage 1 windows; both are off by default.

| Field | Value |
| --- | --- |
| Repository | [UniXNU/ShengUfs](https://github.com/UniXNU/ShengUfs) |
| Hardware | SM8550 UFS host, PHY, clocks and SMMU resources |
| Board dependencies | sheng power policy and storage layout |
| Verified device | sheng native UFS root |
| Runtime class | `NativeUfs` |

The component catalog supplies its kernel archive recipe. The selected device
profile enables `CONFIG_XNU_NATIVE_UFS` and supplies the board inputs.

```sh
./unixnu build kernel -D ../UniXNU-sheng
```

## Porting and records

The sheng device repository supplies ShengUfs as a submodule. Follow the
[UFS porting guide](/porting/ufs) and maintain controller, clock, PHY, SMMU,
DMA, partition and completion details in the [storage record](/devices/sheng#storage).

For the arm64e public-source build path and its current linking/runtime limits, see [public-source driver builds](/porting/migration#source-drivers). Historical iOS 17 device results do not qualify this path.
