# GopFramebuffer

Start with the [adaptation procedure](/porting/display) for board inputs, source changes, build integration and verification order.

Framebuffer presentation using the firmware GOP handoff.

[Source repository](https://github.com/UniXNU/GopFramebuffer).

The implementation reads the firmware framebuffer through PE_current_console and integrates with the selected MobileFramebuffer ABI. Board hooks supply display policy and GPU scanout integration.

Direct display fixes each swap's target at its first successful GPU fence query. Busy or unavailable queries retry after 200 microseconds. A 250-millisecond wait records a slow frame and continues waiting. The previous frame remains displayed until completion or swap cancellation; cancellation clears the retry timer and target.

## Integration

The catalog records implementation scope, hardware and OS requirements, board dependencies, revision, build stage, outputs, and runtime identifiers. The selected profile orders build commands by dependency.

```sh
./unixnu build kernel -D /path/to/device
```

[Component catalog](/reference/components)

Frame diagnostics retain allocation, command, completion and GPU/display timing. Pixel capture is disabled. See [GPU frame diagnostics](/porting/gpu-diagnostics).

Frame diagnostics read physical addresses from prepared direct-display slots. Validation reports zero until mapping, and the flip records the mapped address. Diagnostic observers do not prepare descriptors or query their physical segments.
