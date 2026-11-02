# GPU frame diagnostics

On sheng, add these boot arguments to record GPU work and display decisions:

```text
sheng-gpu-trace=1 sheng-gpu-pixels=1 sheng-diag-export=180
```

The export runs once at the selected number of seconds of boot-log time. With tracing enabled, the default is 180 seconds. The switches do not schedule a reboot. Keep the system running until the export completes, then use the log reader. Normal builds leave tracing disabled.

## Recorded data

| Layer | Data |
| --- | --- |
| Build and configuration | Kernel source ID, Metal source SHA-256, Turnip build ID, process name, single-sample policy, preemption and page-table modes, `TU_DEBUG`. |
| Display wait | Request ID, target fence, both ring completion fences, completed prefix, query result, lock contention, wait duration, timeout and release reason. |
| Display buffers | Surface memory address, dimensions, format, current and pending slots, validation, flip, hardware latch and retirement. |
| Scheduling | PID, requested queue priority, effective priority, task role, ring, submission fence, completion, preemption and recovery. |
| Shared surfaces | IOSurface ID, texture/view, import address and physical page, command use, submit and completion phases, event/fence waits and signals. |
| Render passes | Original and effective samples, attachment and resolve handles, load/store actions, direct destination or resolve copy count. |
| Colour and memory | Metal/Vulkan formats, swizzles, GMEM/sysmem mode, per-attachment state, GMEM transfer sites and colour swap settings. |
| Pixel samples | Completed Poster output, backboardd output and display memory, with dimensions, source stride, format, transfer encoding, surface colour description and profile hash when present. |

Each process numbers its Metal command buffers. Runtime IDs link these numbers to Vulkan command buffers; Turnip links those buffers to kernel fences. IOSurface IDs link producers and consumers across processes. The kernel import records link their mappings to display memory. Shared-event handles currently remain process-local; unsupported cross-process handle requests have their own event.

## Read and decode

`read-sheng-log.py` extracts `diag/files/gpu.trace.bin` and `gpu.pixels.bin`, then writes `diag/gpu/events.jsonl`, `links.jsonl`, `summary.json` and pixel files. To decode an existing export:

```sh
python3 scripts/decode-gpu-trace.py RUN/diag/files
```

These scripts live in UniXNU-sheng and the resolved build tree. `decode-gpu-trace.py` defines the versioned field schema. Events use kernel uptime microseconds; GPU job timestamps retain their hardware tick units. Links use explicit handles and fences. Missing records produce unresolved links rather than inferred dependencies.

The live ring retains 16,384 records. Configuration and active imports have 4,096 metadata slots. Each pixel capture retains the preceding 4,096 records so its trace survives ring wrap. The exporter freezes these records before scanning other diagnostic files. The header reports dropped writes, and the frontend reports failed transport calls.

Pixels are raw sampled grids up to 64 × 64, with at most three captures per process and stage, spaced at least 30 seconds apart. The kernel holds at most 24 captures. Sampling happens after actual completion; direct scanout additionally requires a cleared hardware flush. The copied scanout path samples after the GPU copy acknowledgement. Unsupported layouts record metadata. `.raw` preserves texels; `.json` preserves the layout; `.png` is a preview. Half-float previews clip to 0–1 and encode sRGB. Format transfer encoding and the IOSurface colour-space description are separate fields. A changed CPU sample is flagged.

`gpu-build.json` travels inside the Metal bundle. The image packer's `sheng-uefi-xnu.json` records image and payload SHA-256 values. Keep these files with the export to identify the tested image.

## Checks

```sh
python3 scripts/check-gpu-trace.py
python3 scripts/check-native-adreno-scheduling.py
python3 scripts/build-adreno740-kits.py
python3 scripts/build-gop-legacy-display-27.py
python3 scripts/build-boot-progress.py
python3 scripts/build-turnip-darwin.py --target ios27
python3 scripts/build-adreno-metal-plugin.py --target ios27 --no-replay
```

Run build commands from the prepared sheng iPadOS 27 tree with its toolchain and UEFI input. The host checks cover concurrent ring writes, wrap, pixel ownership and fragment ordering, ABI copies, malformed exports and handle reuse.
