# SoftwareAES

Start with the [adaptation procedure](/porting/platform) for board inputs, source changes, build integration and verification order.

Software AES-CBC through XNU AES helpers and the IOAESAccelerator ABI.

[Source repository](https://github.com/UniXNU/SoftwareAES).

SoftwareAES uses the selected XNU and IOCryptoAcceleratorFamily interfaces.

## Integration

The catalog records implementation scope, hardware and OS requirements, board dependencies, revision, build stage, outputs, and runtime identifiers. The selected profile orders build commands by dependency.

```sh
./unixnu build kernel -D /path/to/device
```

[Component catalog](/reference/components)
