# ShengUfs

Start with the [adaptation procedure](/porting/ufs) for board inputs, source changes, build integration and verification order.

ShengUfs provides the SM8550 UFS storage path. It owns the host
controller, SMMU mappings, command queues, and root reads. Its board integration
includes clock resources and the persistent Data and log regions. On request it
also gives the display bank (`sheng-dpu-scanout`) and the WiFi endpoint
(`sheng-wifi=2` or more) stage 1 windows; both are off by default.

| Field | Value |
| --- | --- |
| Repository | [UniXNU/ShengUfs](https://github.com/UniXNU/ShengUfs) |
| Hardware | SM8550 UFS host, PHY, clocks and SMMU resources |
| Board dependencies | Board power policy and storage layout |
| Verified device | [Reference native UFS root](/devices/sheng#storage) |
| Runtime class | `NativeUfs` |

The component catalog supplies its kernel archive recipe. The selected device
profile enables `CONFIG_XNU_NATIVE_UFS` and supplies the board inputs.

```sh
./unixnu build kernel -D /path/to/device
```

## Porting and records

The device repository supplies ShengUfs as a submodule. Follow the
[UFS porting guide](/porting/ufs) and maintain controller, clock, PHY, SMMU,
DMA, partition and completion details in the [storage record](/devices/sheng#storage).

For the arm64e public-source build path and its current linking/runtime limits, see [public-source driver builds](/porting/migration#source-drivers). Historical iOS 17 device results do not qualify this path.

## Wi-Fi DMA window

The WCN7850 DMA window maps 128 MiB at IOVA 0x10000000 using 64 two-MiB
blocks in its own SMMU context bank. Device checks reach Wi-Fi interface
readiness and traffic with zero DMA allocation failures. The board fixture
`scripts/check-wifi-dma.py` checks capacity and allocation boundaries.
