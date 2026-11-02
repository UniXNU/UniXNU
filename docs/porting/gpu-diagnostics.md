# GPU frame diagnostics

The sheng latency capture records allocation, submission, completion, CPU contention, GPU execution and display timing. Enable it with:

```text
sheng-log=1 sheng-gpu-trace=1 sheng-gpu-perf=1 sheng-diag-export=240
```

The export runs once at the selected boot-log time. These switches do not schedule a reboot. Leave the device running until the export completes, then return to fastboot and read it. Normal builds leave GPU tracing disabled.

## Retained evidence

| Investigation | Records |
| --- | --- |
| Foreground allocation | Pool, requested and available KiB, backing handle, reuse or allocation, page preparation, device-lock duration and caller stack. |
| Background reservation | The same memory-operation IDs and pool fields, with foreground and room-worker roles. |
| Submission delay | Command creation/commit, encoding batch enqueue/start/end, slow encoding operations, runtime lowering, scheduler handoff and Vulkan submission. |
| Release and completion | Deferred physical release, resource/owner destruction, GPU wait return, completion state, handlers, retained objects and final preparation. |
| Concurrent services and faults | Process CPU time, CPU occupancy, touch intervals, target/peer thread stacks, Mach requests/replies, exceptions, registers, image UUIDs and fatal exit reasons. |
| GPU execution | Per-pass hardware duration, dimensions, render mode, attachment conditions, shader figures, submission/fence identities and valid A7XX counter intervals. |
| Upstream display gaps | Validation, GPU wait, flip, latch, retirement and blanking, joined with render-thread and service-peer waits. |

Kernel/Metal/Turnip build identities, process names, runtime configuration, queue/ring transitions and record-coverage counts accompany these records.

## Collection policy

GPU tracing excludes texture/view inventories, colour-transfer sites, pixel samples and screen images. It retains command/pass identities and synchronization. Repeated pending display queries retain state changes, a 100 ms heartbeat and an omitted-query count; completion is retained. Idle runtime sleep/wake and scheduler-turn stages are excluded before recording.

IPC retains traced requests, their matching receives and replies on tracked reply ports. Unmatched receives are counted. The tracker is bounded and nonblocking; table saturation or ambiguous reply-port reuse increments its coverage counter. The duplicate IPC stream and general IOKit/GPU-call rings are not collected. Command submission timing and allocation-specific driver phases remain available.

Fast resource release spans below 250 microseconds are omitted. Completion and owner callbacks retain their paired records. CPU occupancy, process CPU totals, slow encoding operations and blocked-thread sampling provide CPU context without suspending the render thread for a separate 2 ms profiler.

LAT1 reserves 32,768 slots for faults, exit reasons and process identities, with 491,519 slots for ordinary latency events and one summary record. High-rate ordinary events cannot overwrite the fault lane. The summary reports issued/retained counts for both lanes, unmatched IPC and tracking failures. Decoders report coverage before attribution.

## Export contents

The exporter prioritizes the complete backboardd `frames.trace`, then the CPU, allocation, touch and kernel timing evidence. It includes at most two crash reports per named service or widget process, within an 8 MiB crash-report budget. Exception records retain the current capture's fault state independently of these files.

The export omits shader-cache inventories and priming journals, framework files, general unified logs, screenshots and pixel grids. The periodic text slot records capture identity and timing. Its message-buffer copy retains fault, memory-pressure and relevant service diagnostics. `diag-skipped.txt` identifies files that did not fit.

## Read and decode

Run from UniXNU-sheng or the resolved sheng build tree:

```sh
fastboot boot /path/to/sheng-linux-log.img
python3 scripts/read-sheng-log.py --wait 60 --out /path/to/logs
```

The reader returns the device to fastboot and writes `diag/gpu/events.jsonl`, explicit command/fence links, `diag/latency.jsonl`, a latency analysis and decoded frontend records. Decode saved files with:

```sh
python3 scripts/decode-gpu-trace.py RUN/diag/files
python3 scripts/decode-sheng-latency.py RUN/diag/files/kernel.latency.bin --out RUN/latency.jsonl --frames RUN/diag/files/private/var/mobile/Library/Caches/com.apple.backboardd/m2v/frames.trace
```

LAT1 is a 16-byte header followed by 72-byte records. Capture summary event 34 describes the separate retention lanes. Event 33 links a received reply to its request. GPU display-wait records include the number of repeated queries omitted. Frontend records retain complete command summaries, batch/commit phases, runtime memory decisions and per-pass hardware timings.

CPU events use kernel uptime. GPU pass timestamps use a hardware clock; their duration can be measured within that clock, while absolute alignment to CPU events requires calibration. Match identities explicitly. Compare touch-active intervals and matching scenes separately from idle and lock transitions.

`sheng-gpu-perf=1` enables the 19-counter A7XX BR capture with GPU DCVS and diagnostics. Raw values include selector readback, torn-read, reset and preemption validity. Derived deltas use valid intervals only. These counters describe global GPU intervals; pass timing supplies workload context.

## Checks

```sh
python3 scripts/check-gpu-trace.py
python3 scripts/check-native-adreno-scheduling.py
```

The host checks exercise event selection before transport, pending-query coalescing, request/reply tracking, capture coverage, fault isolation, compiler-stage filtering and decoder schemas. Build the affected kernel, display and Metal components from the prepared sheng iPadOS 27 tree for the target ABI.
