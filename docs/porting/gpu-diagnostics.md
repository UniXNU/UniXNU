# GPU frame diagnostics

The reference latency capture records only the evidence for seven frame-latency questions: foreground allocation, background reservation, submission delay, release and completion, concurrent services and faults, GPU pass cost, and upstream display gaps. Enable it with:

```text
sheng-log=1 sheng-gpu-trace=1 sheng-gpu-perf=1 sheng-diag-export=240
```

The export runs once at the selected boot-log time. These switches do not schedule a reboot. Leave the device running until the export completes, then return to fastboot and read it. Normal builds leave GPU tracing disabled.

## Retained evidence

| Investigation | Records |
| --- | --- |
| Foreground allocation | Pool, requested and available KiB, backing handle, reuse or allocation, page preparation, device-lock duration and caller stack. |
| Background reservation | The same memory-operation IDs and pool fields, with foreground and room-worker roles. |
| Submission delay | Command creation/commit, encoding batch enqueue/start/end, slow encoding operations, runtime lowering, scheduler handoff, Vulkan submission, and 4 ms samples of the render server's encode thread. |
| Release and completion | Deferred physical release, resource/owner destruction, GPU wait return, completion state, handlers, retained objects, final preparation, and 4 ms samples of the completion thread. |
| Concurrent services and faults | Process CPU time, CPU occupancy, the busiest threads, exceptions, registers, image UUIDs, fatal exit reasons, crash reports of the named services, and shared-region unnests with their kernel and user callers. |
| GPU execution | Per-pass hardware duration, dimensions, render mode, attachments (surface, size, format, load/store), shader figures, submission/retirement, GPU frequency votes and valid A7XX counter intervals. |
| Upstream display gaps | Validation, GPU wait, flip, latch, retirement and blanking; 4 ms samples of the render server's render thread and SpringBoard's main thread; blocked-thread waits with their Mach peers. |

Touch report times bound the analysed intervals.

## Collection policy

The kernel GPU ring holds submission, retirement, display arrival, display fence and latch, build identities and the render server's render, encode and completion thread identities. Other processes send nothing to it. Everything else of the render server goes to its own `frames.trace`, without a system call per record.

Mach message streams, user-client call rings, contiguous allocation rings, per-contact touch records, dispatch introspection, queue-priority, ring-switch, restart and stall rows, other processes' pass and pipeline notes, status and telemetry lines, screenshots and pixel samples are not collected.

Fast resource release spans below 250 microseconds are omitted. Completion and owner callbacks retain their paired records.

LAT1 reserves 32,768 slots for faults, unnests, exit reasons and process identities, with 491,519 slots for ordinary latency events and one summary record. Ordinary events cannot overwrite the fault lane.

## Export contents

The exporter writes `gpu.trace.bin`, `kernel.latency.bin`, `kernel.rings.txt` (swap ring, GPU timeline, sampler targets, process names, scanout waits), `kernel.boalloc.bin`, `kernel.cpus.bin`, `kernel.ptime.bin`, `kernel.touch.bin`, `kernel.client.bin`, the backboardd `frames.trace`, and at most two crash reports per named service or widget process within 8 MiB. Its message-buffer copy retains fault, memory-pressure and named-service lines. `diag-skipped.txt` lists files that did not fit and the lookup result of dasd's model resource.

## Read and decode

Run from the reference device repository or its resolved build tree:

```sh
fastboot boot /path/to/linux-log.img
python3 scripts/read-sheng-log.py --wait 60 --out /path/to/logs
```

The reader returns the device to fastboot and writes `diag/gpu/events.jsonl`, `diag/latency.jsonl`, its analysis, the decoded frontend records, the touch windows and the `*.touch.*` outputs limited to them. Decode saved files with:

```sh
python3 scripts/decode-gpu-trace.py RUN/diag/files
python3 scripts/decode-sheng-latency.py RUN/diag/files/kernel.latency.bin --out RUN/latency.jsonl \
  --frames RUN/diag/files/private/var/mobile/Library/Caches/com.apple.backboardd/m2v/frames.trace \
  --touch RUN/diag/files/kernel.touch.bin
```

LAT1 is a 16-byte header followed by 72-byte records. Events 35 and 36 are an unnest's range, user registers and kernel callers; its user stack follows as fault events 8, 9 and 12 with the same ID. Client sampler records carry the sampled role in state bits 12-13 (1 render, 2 encode, 3 completion).

CPU events use kernel uptime. GPU pass timestamps use a hardware clock; their duration can be measured within that clock, while absolute alignment to CPU events requires calibration.

`sheng-gpu-perf=1` enables the 19-counter A7XX BR capture with GPU DCVS and diagnostics. Derived deltas use valid intervals only. These counters describe global GPU intervals; pass timing supplies workload context.

## Checks

```sh
python3 scripts/check-gpu-trace.py
python3 scripts/check-native-adreno-scheduling.py
```
