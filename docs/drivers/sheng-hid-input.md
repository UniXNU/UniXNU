# ShengHidInput

Start with the [adaptation procedure](/porting/input) for board inputs, source changes, build integration and verification order.

Touch and button integration with IOHIDFamily.

[Source repository](https://github.com/UniXNU/ShengHidInput).

The implementation uses the board touch state and the IOHIDFamily 2031.120.4 ABI. Its archive builder reads a qualified prelinked candidate and its ABI records. Board touch policy and the selected OS ABI are required inputs.

## Integration

The catalog records implementation scope, hardware and OS requirements, board dependencies, revision, build stage, outputs, and runtime identifiers. The selected profile orders build commands by dependency.

```sh
./unixnu build kernel -D /path/to/device
```

[Component catalog](/reference/components)

For the arm64e public-source build path and its current linking/runtime limits, see [public-source driver builds](/porting/migration#source-drivers). Historical iOS 17 device results do not qualify this path.

## Original-time touch history

The source-IOHID sender receives ordered snapshots with their original observation ticks. It preserves first-contact history through confirmation and emits explicit tip-up records for vanished IDs. Snapshot ACK follows successful handleReportWithTime submission; partial success of a split transition is committed per packet. Same-ID coordinate updates preserve a continuous touch.

The board producer and HID sender are a coordinated interface. The old unverified timestamp ABI is not substituted, and an API ACK is not a user-space delivery guarantee. See the Novatek driver page for typed observation processing and the device input record for the exact evidence scope.
