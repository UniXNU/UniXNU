# QcomGeniSpi

Start with the [adaptation procedure](/porting/input) for board inputs, source changes, build integration and verification order.

Qualcomm GENI serial-engine SPI controller operations.

[Source repository](https://github.com/UniXNU/QcomGeniSpi).

Callers provide register access and platform callbacks. The reference touch stack uses this component with ShengNovatekTouch. Match controller resources and callback requirements when reusing it.

## Integration

The catalog records implementation scope, hardware and OS requirements, board dependencies, revision, build stage, outputs, and runtime identifiers. The selected profile orders build commands by dependency.

```sh
./unixnu build kernel -D /path/to/device
```

[Component catalog](/reference/components)
