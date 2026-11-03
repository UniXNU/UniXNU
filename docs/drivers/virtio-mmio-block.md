# VirtioMmioBlock

Start with the [adaptation procedure](/porting/platform) for board inputs, source changes, build integration and verification order.

VirtIO 1.2 MMIO block transport using split queues.

[Source repository](https://github.com/UniXNU/VirtioMmioBlock).

The component requires a compatible MMIO device, interrupt routing, and the selected storage ABI. The owner-root path also supplies its verified block policy archive.

## Integration

The catalog records implementation scope, hardware and OS requirements, board dependencies, revision, build stage, outputs, and runtime identifiers. The selected profile orders build commands by dependency.

```sh
./unixnu build kernel -D /path/to/device
```

[Component catalog](/reference/components)
