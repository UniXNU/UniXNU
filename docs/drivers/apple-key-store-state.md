# AppleKeyStoreState

Start with the [adaptation procedure](/porting/platform) for board inputs, source changes, build integration and verification order.

AppleKeyStore state queries and state hooks for the selected userland ABI.

[Source repository](https://github.com/UniXNU/AppleKeyStoreState).

The component handles AppleKeyStore selectors and the state callbacks used by the selected OS profile. Its runtime service and symbols are recorded in the catalog.

Key wrapping is software: the device key derives from the identity the board returns through `native_aks_device_id`, and the keychain uses it to store and read items. This is not hardware data protection. Reference key operations and device lock are unsupported.

On iPadOS without a keybag the board sets `aks-sls=3`, which reports no passcode. On macOS the device lock state stays at `0` (unlocked) while per-user session handles (`< -3`, such as `-501`) return `kIOReturnNotFound` so `MobileKeyBag` reports `NotFound` (`-8`) instead of claiming an empty passcode or a missing per-user SEP keybag.

## Integration

The catalog records implementation scope, hardware and OS requirements, board dependencies, revision, build stage, outputs, and runtime identifiers. The selected profile orders build commands by dependency.

```sh
./unixnu build kernel -D /path/to/device
```

[Component catalog](/reference/components)
