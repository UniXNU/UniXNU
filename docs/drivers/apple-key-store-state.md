# AppleKeyStoreState

Start with the [adaptation procedure](/porting/platform) for board inputs, source changes, build integration and verification order.

AppleKeyStore state queries and state hooks for the selected userland ABI.

[Source repository](https://github.com/UniXNU/AppleKeyStoreState).

The component handles AppleKeyStore selectors and the state callbacks used by the selected OS profile. Its runtime service and symbols are recorded in the catalog.

## Integration

The catalog records implementation scope, hardware and OS requirements, board dependencies, revision, build stage, outputs, and runtime identifiers. The selected profile orders build commands by dependency.

```sh
./unixnu build kernel -D /path/to/device
```

[Component catalog](/reference/components)
