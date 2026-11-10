# GPU frame diagnostics

The reference latency capture records only the evidence for seven frame-latency questions: foreground allocation, background reservation, submission delay, release and completion, concurrent services and faults, GPU pass cost, and upstream display gaps. Enable it with:

```text
log=1 gpu-trace=1 gpu-perf=1 diag-export=240
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

## Board rows without tracing

`log=1` with `log-gpu=1` prints these rows in every board log slot, without
`gpu-trace`. `diag=1` keeps them and adds the latency lines of the kernel
messages of each round as `[diag msgs]`.

| Row | Content |
| --- | --- |
| `[gpu jobs]`, `[gpu long]`, `[gpu slow]` | Jobs over 8, 16, 33 and 100 ms, the eight longest jobs and the newest jobs over 8 ms, each with process, queue, ring, priority, IB count and size. `gpu-timeline=1` takes the durations from CP timestamps; otherwise they are an upper bound from the driver's clock. |
| `[gpu kick]` | The CP's IB position at the first timed-out wait, at the stall stage and 500 microseconds later, and when the job retired. A position that never moved is a stuck CP; one that moved is a long job. |
| `[gpu pool views]` | Viewed pool grants tracked through the kernel's last-unmap report, and their pages returned to the pool. |
| `[log round]` | The last and longest round of the board log writer and its slowest step. A round over 10 s is reported in the kernel log, and a panic names the step a round was in. |

`gpu-audit=1` runs the CPU cache line audits of submitted IBs and synchronized
buffers. They only detect stale lines; the write-combining correction runs on
every submission either way.

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

The sheng sampler walks a remote kernel stack only while the target is waiting, off the run queue and past switch-out, with its scheduler lock held. An empty kernel stack in a sample can mean the thread was switching out or its saved registers were unavailable. The wait event and thread state remain available.

CPU events use kernel uptime. GPU pass timestamps use a hardware clock; their duration can be measured within that clock, while absolute alignment to CPU events requires calibration.

`gpu-perf=1` enables the 19-counter A7XX BR capture with GPU DCVS and diagnostics. Derived deltas use valid intervals only. These counters describe global GPU intervals; pass timing supplies workload context.

For sheng captures with `cpufreq=4`, match the governor votes and EPSS domain readbacks in `kernel.cpufreq.bin` to the CPU uptime of each flip. On this board, CPUs 0 to 2, 3 to 6 and 7 belong to distinct frequency domains. In `kernel.client.bin`, peer −2 marks a user PC and LR captured by interrupting the running thread. With CLI1 header flag 1, the wait-event slot in those samples contains the interrupted CPU number. Older exact samples do not identify the CPU. Set `cs-exact=0` to disable the cross-core sampler. With `cs-exact=1 cs-profile=1`, only the SpringBoard main thread receives sampling IPIs. The board samples two available Arm PMUv3 counters for EL0 retired instructions and cycles on the interrupted CPU. The general XNU CPU counter facility stays disabled. A missing PMU, a trapped register, insufficient events and occupied counters have distinct statuses. Use only pairs on the same CPU and thread with the same context-switch count.

The profile also records SpringBoard main-thread Mach calls lasting at least 250 µs, including the destination PID, message ID, start of the receive phase and return status. An ordinary receive has no designated sender. The export marks a call still pending when the capture ends. Decode the data and sampler cost with `python3 scripts/sheng-springboard-profile.py kernel.latency.bin`.

Run `python3 scripts/sheng-latency-report.py RUN/diag --frames-only` in the device repository to compare HID cadence and flip intervals across boots using only the HID and flip rings. Its continuous subset includes both flip boundaries when checking for gaps in HID reports.

## Checks

```sh
python3 scripts/check-gpu-trace.py
python3 scripts/check-native-adreno-scheduling.py
```
