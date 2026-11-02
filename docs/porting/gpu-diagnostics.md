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

Display-fence reasons are: 0, no linked GPU fence provider; 1, target completed; 2, wait reached 250 milliseconds; 3, target pending; 4, query unavailable, retry scheduled. Reasons 2, 3 and 4 keep the current frame displayed. `query_reason` distinguishes an unpublished provider (0), lock contention (1), a successful query (2), an unavailable progress result (3), and the legacy interface (4).

With `sheng-wallpaper-freeze=1`, event 60 (`wallpaper_freeze`) records phase, command, surface ID, frozen command, freeze time in microseconds, admitted count and parked count. Phases are 0 enabled, 1 admitted, 2 frozen after GPU completion, and 3 parked without runtime submission. Match the renderer PID to kernel submission events to check that new GPU work stops after the transition; work admitted earlier may still complete.

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

## CPU latency records

Events 61, 62 and 63 identify encoding batches, frontend command phases and named threads. Batch records retain enqueue time, queue depth, task count and start/end times. Command phases distinguish submit, surface flush, runtime commit, resource release and completed handlers. `frames.trace` types 14 and 15 retain the same phases; type 16 retains pass attachment load/store, sample count, format, size and IOSurface ID. Runtime stages 40 through 52 record pool, KiB, reuse, allocation, cache and physical release decisions. Stages 53 through 57 split completion processing into state collection, handlers, retained resources and final preparation. Memory operation IDs are separate from command-buffer IDs.

`kernel.latency.bin` uses a 16-byte `LAT1` header with total, retained and dropped counts, followed by 72-byte records. Its 524,288 slots retain IPC send attempts and receive completions with the same kernel message cookie, user exception codes and PC/LR/SP, GPU frequency votes, and touch publications with contact IDs and coordinates in tenths of a pixel. Match IPC by cookie, destination and message ID within the retained window. A send attempt alone does not establish delivery. Accepted GPU levels are votes acknowledged by the governor; they are not a measured frequency counter.

```sh
python3 scripts/decode-sheng-latency.py RUN/diag/files/kernel.latency.bin --out RUN/latency.jsonl
```

Tracing starts after 50 display flips with diagnostic export enabled. Writers never wait for a trace slot. The exporter snapshots this ring before file collection and prioritizes crash reports over framework and unified-log files. Client samples mark a selected Metal render thread with state bit `0x1000`; the thread identity comes from event 63. Process CPU records refresh an `xpcproxy` name after exec. Compare continuous touch intervals and matching scenes separately from idle and lock transitions.

## Detailed latency capture

Frontend types 17 and 18 record encoding operations of at least 250 microseconds, closure release, individual completion handlers, resource destruction and owner deallocators. Release spans cover buffers, textures, functions, libraries, pipelines, samplers, state, events, fences, encoders, command buffers, queues, heaps and binary archives. Each record carries operation, command, object or callback address, thread, source line, enqueue time and parent task identity. Type 19 and event 67 define operation labels. Event 64 carries the same timing through the kernel trace.

IPC records include outgoing requests, destination task and port, and reply-port identity. Process records map task pointers to PIDs and names. The capture worker samples blocked threads of backboardd and SpringBoard every 100 ms and follows up to two Mach service peers. It scans up to 128 threads and emits up to six changed waiters per process and round. Unchanged waits have a one-second heartbeat. Records include user/kernel stacks, wait object, context switches, Mach peer and coverage counts. Dispatch introspection v2 adds enqueue, dequeue, completion, parent-task and queue-label records when that SPI is available. Its status identifies an absent symbol or unsupported layout.

Mach exceptions retain PC/LR/SP/FP, FAR/ESR and all 29 general registers. A bounded 32-entry queue lets the capture worker read up to 32 frames, 128 stack bytes, shared-cache UUID and up to 64 image UUIDs. Records report read errors, truncation and capture delay. Fatal signal exits also retain reason namespace, code, process name and a 96-byte description. Exception registers describe the trap; worker stack reads have their own capture time.

`sheng-gpu-perf=1`, with GPU DCVS and diagnostic export enabled, samples 19 A7XX BR counters on the governor worker every two ticks, approximately 32 ms. The plan covers GPU clocks, UCHE latency/read beats/stalls, texture-cache requests/misses, shader activity/instructions and colour read/write data. Selector readback, torn reads, counter resets and preemption epochs accompany raw values. The decoder derives deltas only across valid intervals. These are global BR intervals; command/pass timing supplies the workload context. Register and countable definitions are checked against the pinned Mesa XML.

```sh
python3 scripts/decode-sheng-latency.py RUN/diag/files/kernel.latency.bin --out RUN/latency.jsonl --frames RUN/diag/files/private/var/mobile/Library/Caches/com.apple.backboardd/m2v/frames.trace
```

The reader writes decoded records, an analysis JSON with IPC/task links, counter deltas and fault snapshots, and frontend detail records. The selected source-storage archive includes `BootLatencyTrace.c` and records its header hashes.
