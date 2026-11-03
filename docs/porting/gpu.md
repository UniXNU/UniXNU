# GPU and Metal adaptation

Complete [platform DMA](/porting/platform) and basic [display presentation](/porting/display)
first. Read the [Adreno740 runtime path](/drivers/adreno740) and
[AdrenoMetal interface](/drivers/adreno-metal).

Use [driver build integration](/porting/drivers#build-integration) to connect
initialization, archive recipes and the OS ABI, then run this page's hardware checks.

## Sources and interfaces {#source-map}

These links identify reviewed source revisions. Match interfaces to the selected
SoC, component and OS versions. The linked device sources provide board integration
examples.

| Implementation | Source | What to read and implement |
| --- | --- | --- |
| Power and firmware | [NativeAdrenoGmuPlatform.h](https://github.com/UniXNU/Adreno740/blob/1030485546ef7ebb9abbfb7c17fbca93cca40971/NativeAdrenoGmuPlatform.h#L15), [build-adreno740-kits.py](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/scripts/build-adreno740-kits.py) | `NativeAdrenoGmuPlatform::bind/services`, mapped windows, timers and firmware inputs |
| Submission and memory | [NativeAdrenoClient.h](https://github.com/UniXNU/Adreno740/blob/1030485546ef7ebb9abbfb7c17fbca93cca40971/NativeAdrenoClient.h#L14), [NativeAdrenoVm.h](https://github.com/UniXNU/Adreno740/blob/1030485546ef7ebb9abbfb7c17fbca93cca40971/NativeAdrenoVm.h) | `NativeAdrenoTransport`, BO lifetime, GPU mappings and completion |
| OS/frontend interface | [NativeOfflineAccelerator.cpp](https://github.com/UniXNU/AdrenoMetal/blob/816022307852de7e1741ac05ae9111982318763f/NativeOfflineAccelerator.cpp), [OfflineMetalWire.h](https://github.com/UniXNU/AdrenoMetal/blob/816022307852de7e1741ac05ae9111982318763f/OfflineMetalWire.h) | Accelerator publication and request structures used by the matching frontend |

## 1. Match the GPU generation and OS ABI

Adreno740 implements the A740 kernel interface. AdrenoMetal uses that interface,
Turnip, metal2vulkan and the selected OS GPU/IOSurface ABI. Identify the target
GPU revision and compare register, firmware, packet and memory interfaces.
For another GPU generation, implement the matching kernel backend and compiler
support before selecting its frontend.

For another A740 board, collect GPU/GMU registers, interrupts, SMMU context and
stream IDs, firmware, power domains, clock/voltage levels, interconnect votes,
RAM reservations and scanout layout. Check them against the selected firmware.

## 2. Adapt power and firmware inputs

Read the [SM8550 platform sources](https://github.com/UniXNU/UniXNU-sm8550-common/tree/main/kits)
and the [reference board package](https://github.com/UniXNU/UniXNU-sheng/tree/main/package).
`Sm8550Platform` supplies shared GMU operations and command-database handling.
`ShengGmuVotes.c` and `ShengGmuVotesSource.h` supply the board's OPP and bandwidth
policy. Port those inputs to the target's rails and command database.

The reference recipe `scripts/build-adreno740-kits.py` embeds these local inputs:

| Firmware | Purpose |
| --- | --- |
| `qcom/gmu_gen70200.bin` | GMU image |
| `qcom/a740_sqe.fw` | Command processor firmware |
| `qcom/sm8550/sheng/a740_zap.mbn` | Board's signed ZAP image |

The recipe checks pins in `scripts/data/adreno-inputs.json` and reads
`.cache/firmware/sheng-gpu/`. Adapt the extraction paths and pins to the target's
verified firmware; record provenance in `proprietary-files.txt`.

**Expected result:** board power inputs and firmware match the target GPU.
Confirm GMU startup and HFI response before submitting commands.

## 3. Establish memory and command submission

1. Review ArmSmmu4K context ownership, stream selection, address width and cache
   maintenance. Use the target GPU and firmware stream IDs from its hardware description.
2. Adapt reserved memory and GPU virtual-address windows. Keep scanout, firmware,
   ring and client allocations within their owned ranges.
3. Confirm CP initialization, ring progress and fence completion with bounded work.
4. Render a known image and inspect the result before using UI workloads.
5. Verify client teardown, mapping lifetime and fence failures.

Use `AdrenoFirmware` for firmware/HFI operations and `AdrenoPM4` for supported
packet encoding. The reference recipe links these kits, ArmSmmu4K and board votes
into `libAdreno740.a`, then builds the accelerator through
`build-adreno740-accelerator.py`. Preserve that order when creating the target recipe.

**Expected result:** commands complete, fences advance and the known image is
correct. Record GPU results independently from desktop presentation.

### Keep mapping and submission cheap {#memory-path}

A desktop frame allocates, maps and frees many buffers, so per-call cost decides
smoothness. Adreno740 and ArmSmmu4K use these rules; keep them when porting:

| Operation | Rule |
| --- | --- |
| Object lookup | A client's objects are limited by memory and found through a handle index. |
| Allocation | BOs come from system memory: a pageable `IOBufferMemoryDescriptor` with no task and the write-combined cache mode, wired by `prepare()`. The VM sets the page attribute in one batch and restores it on free; client views map that descriptor. Only a caller that asks for contiguous memory gets a contiguous kernel allocation. |
| Map of owned memory | `ArmSmmu4KLiveMapContextBatchExclusive`: no alias check against the existing ranges. |
| Map of imported memory | The same call when every mapped import shares its cache class and none of its pages is in a BO of this driver (a page bitmap over DRAM); otherwise the fully checked batch map. |
| Unmap | Up to 512 pages: one TLBIVAL per page. Larger: invalidate the ASID. |
| Submission | No TLB invalidation. A map fills only invalid leaves, an unmap invalidates its own pages, and the upper tables never change. A stalled fence still invalidates. |

The boot log's `[vm map]`, `[vm unmap]`, `[vm kinds]` and `[bo memory]` rows give
the count and time of each operation. Compare them before and after a change.

With `NativeAdrenoClient`, implement one bounded submission in this order:
query ABI/capabilities, allocate a BO, map it to an allowed IOVA, populate commands,
submit and wait for the returned fence. Bind `NativeAdrenoTransport.call` to the
actual kernel dispatcher, preserving each request's input/output sizes. Synchronize
caches before CPU readback. On fence timeout, stop the queue and confirm DMA has stopped
before releasing the BO and mapping. Report the failed request, handle and fence
to distinguish allocation, mapping and execution failures.

### Scheduling and memory reuse {#scheduling}

The reference enables mode 2 with `sheng-gpu-preempt=2`. High, normal-high and real-time requests use ring 0; normal, low, background and unspecified requests use ring 1. The task's GPU role selects its foreground or background request. Queues preserve FIFO across priority changes; preemption saves GMEM and restores each ring's executed page table. See [Adreno740 scheduling](/drivers/adreno740#scheduling).

Runtime scheduling and completion threads use interactive QoS on iOS as well as macOS. The encoding thread adopts the render thread's scheduling policy and priority when that reference has a fixed policy.

Unused owned image backing serves later pooled and dedicated images. The room worker takes a suitable spare before allocating another block. Spares age after ten seconds and are reclaimed on allocation failure or memory pressure. Plain unused backing can be released by the room worker; imported memory and owner callbacks keep their release ordering.

### Render mode with an 8-bit BGRA framebuffer {#render-mode}

With `sheng-fb-bgra=1`, the default is `TU_DEBUG=sysmem,nocb`. Passes with an unbacked, lazily allocated transient attachment use GMEM when the render-pass constraints allow it. Other passes keep the system-memory policy. The recorded `turnip-transient-attachments-in-gmem.patch` applies this choice before the SYSMEM override, so memoryless attachments can remain in tile memory.

`turnip-gmem-mutable-swap.patch` preserves colour byte order on GMEM loads and stores. Attachment sizes, row padding, formats and load/store actions remain part of render-mode selection. `sheng-tu-debug=` selects an explicit experiment. Concurrent binning stays disabled.

Metal clients use one sample by default. `NATIVE_METAL_SINGLE_SAMPLE=0` preserves the requested sample count; texture types, pipeline counts and resolve handling follow that policy.

### Find where a slow frame goes {#frame-path}

Enable [frame diagnostics](/porting/gpu-diagnostics) and join the same command, allocation, fence and display request across stages. CPU events use uptime; align GPU timestamps through clock calibration.

| Segment | Evidence |
| --- | --- |
| Creation to commit | Caller work, texture allocation and page preparation. |
| Commit to encoding | Batch enqueue/start/end and slow encoding operations. |
| Encoding to runtime commit | Surface flush and runtime handoff phases. |
| Runtime commit to submission | Prepared/handed/taken stages, held-batch reasons and kernel submission. |
| Submission to GPU completion | Queue/ring timeline, CP timestamps and per-pass hardware duration. |
| Completion to handlers | State collection, frontend cleanup, handlers, retained-resource release and gate preparation. |
| Display update | Validation, fence wait, flip, latch, retirement and blanking. |

Compare matching touch-active scenes separately from static desktop and lock transitions. Record cache build identity and priming progress, event-retention ranges and omitted counts. Global GPU counters describe their sampled interval; per-pass timing identifies the work.

## 4. Build and stage Metal

Build from the resolved target tree with its SDK, compiler dependencies and ABI inputs. For iOS 17:

```sh
python3 scripts/build-turnip-darwin.py --target ios
python3 scripts/build-adreno-metal-plugin.py --target ios
python3 scripts/make-gpu-addon.py --publish build/gpuaddon.bin
```

For iOS 27:

```sh
python3 scripts/build-turnip-darwin.py --target ios27
python3 scripts/build-adreno-metal-plugin.py --target ios27
ADRENO_PLUGIN_DIR=build/adreno-metal-plugin27 python3 scripts/make-gpu-addon.py --publish build/gpuaddon.bin
```

Pass the addon and its matching owner trust bundle to the payload with `--gpu-addon` and `--owner-trust-cache`, and enable the board's addon loader (`sheng-gpu-addon=1` in the reference). Keep the existing Data seed so its persistent data and caches retain their identity. See [packaging](/porting/packaging). The runtime plugin name is `NativeAdrenoMetal`.

Check the selected OS profile's sandbox, user-client and trust-cache integration.
The Metal bridge never returns a nil encoder: a pass it cannot encode gets an
encoder whose command buffer is refused, because RenderBox caches the encoder's
methods. The process's first problem appears on the driver's per-process text
line (`[gpu client text]` in the boot log).
AirNir is the offline compiler kit; the runtime frontend uses the
AIR → SPIR-V → NIR → IR3 chain described in the component page.

**Expected result:** Metal device discovery, client connection, pipeline creation,
rendering and presentation each succeed. Record firmware, compiler and plugin
revisions with the frame result. Cold pipeline compilation and cache reuse need
separate timing observations.

### Warm the shader caches {#shader-warmup}

A pipeline compiles from Apple's AIR the first time something asks for it, which stalls frames. Warm the caches ahead so the desktop finds them. Use `--target ios` for iOS 17 and `--target ios27` for 27. Supply the library list and cache pack for that OS image and compiler build.

1. **Priming list.** Write the absolute path of every `.metallib` of the OS image, one per line, as the render server sees it (`/System/Library/...`). Keep it in `build/prime-list.txt`; `build-adreno-metal-plugin.py` embeds it in the plugin as the `__DATA,__primelist` section, and `make-gpu-addon.py --prime-list FILE` ships it as `addons/NativeAdrenoMetal.primelist`. With a list the render server does not scan directories: its sandbox hides most of them.
2. **Pipeline pack.** Boot an image built with `make-gpu-addon.py --cache-export`; the plugin writes its cache directory to the board log. Read the run with `scripts/read-sheng-log.py`, merge one or more exports with `scripts/make-m2vpack.py OUT EXPORT_DIR...` (later directories win) and ship the result with `make-gpu-addon.py --pipeline-pack OUT`. The plugin imports the pack into the cache directory before the runtime opens it.

How priming runs:

- It starts 90 s after the render server opens the device, on a background thread with an 8 MiB stack.
- Each kernel function becomes a compute pipeline. Each vertex function becomes a render pipeline with the fragment function of the same stem (`_vert_` to `_frag_`) and one BGRA8 attachment. Pipelines made later with other constants or attachments still compile on demand.
- It waits while the desktop animates: more than 8 command buffers in 250 ms is busy, and the idle desktop at 120 Hz submits about 6. After an animation it waits 2 s of quiet, and it never waits longer than 10 s, so one pipeline still compiles on a desktop that never settles.
- Progress lives in the cache directory: `prime-done` (finished libraries), `prime-fn` (finished functions of libraries not finished yet), `prime-current` (the function being compiled), `prime-bad` (functions that ended the process; a start that finds `prime-current` moves it there) and `prime.log`. A restart resumes inside a library with thousands of functions.
- Each finished entry carries the build id: the runtime's translator build plus the Turnip library's `LC_UUID`. A runtime or Turnip rebuild primes every library again; a plugin rebuild alone keeps the work.
- Read `prime-done`, `prime-fn` and `prime.log` to check completed libraries and functions. The focused latency export omits these files; collect them separately when verifying priming.

**Expected result:** completed entries cover the library list for the current build, and a second boot reuses the same scene pipelines. Record the list size, the build id and the cold and warm frame timings.

## Next step

Continue with [Wi-Fi](/porting/network), or return to the
[driver checklist](/porting/drivers).
