# GPU and Metal adaptation

Complete [platform DMA](/porting/platform) and basic [display presentation](/porting/display)
first. Read the [Adreno740 runtime path](/drivers/adreno740) and
[AdrenoMetal interface](/drivers/adreno-metal).

Use [driver build integration](/porting/drivers#build-integration) to connect
initialization, archive recipes and the OS ABI, then run this page's hardware checks.

## Sources and interfaces {#source-map}

These links identify reviewed source revisions. Match interfaces to the selected
SoC, component and OS versions. Files in `UniXNU-sheng` provide board integration
examples.

| Implementation | Source | What to read and implement |
| --- | --- | --- |
| Power and firmware | [NativeAdrenoGmuPlatform.h](https://github.com/UniXNU/Adreno740/blob/4e0314df8ad29d52f6fa3f9383a540adcd618b87/NativeAdrenoGmuPlatform.h#L15), [build-adreno740-kits.py](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/scripts/build-adreno740-kits.py) | `NativeAdrenoGmuPlatform::bind/services`, mapped windows, timers and firmware inputs |
| Submission and memory | [NativeAdrenoClient.h](https://github.com/UniXNU/Adreno740/blob/4e0314df8ad29d52f6fa3f9383a540adcd618b87/NativeAdrenoClient.h#L14), [NativeAdrenoVm.h](https://github.com/UniXNU/Adreno740/blob/4e0314df8ad29d52f6fa3f9383a540adcd618b87/NativeAdrenoVm.h) | `NativeAdrenoTransport`, BO lifetime, GPU mappings and completion |
| OS/frontend interface | [NativeOfflineAccelerator.cpp](https://github.com/UniXNU/AdrenoMetal/blob/454ff2ce83766ce7b3e0f355e83f1d72907708b3/NativeOfflineAccelerator.cpp), [OfflineMetalWire.h](https://github.com/UniXNU/AdrenoMetal/blob/454ff2ce83766ce7b3e0f355e83f1d72907708b3/OfflineMetalWire.h) | Accelerator publication and request structures used by the matching frontend |

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
and the [sheng package](https://github.com/UniXNU/UniXNU-sheng/tree/main/package).
`Sm8550Platform` supplies shared GMU operations and command-database handling.
`ShengGmuVotes.c` and `ShengGmuVotesSource.h` supply the board's OPP and bandwidth
policy. Port those inputs to the target's rails and command database.

The sheng recipe `scripts/build-adreno740-kits.py` embeds these local inputs:

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
packet encoding. The sheng recipe links these kits, ArmSmmu4K and board votes
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

### Render mode with an 8-bit BGRA framebuffer {#render-mode}

With `sheng-fb-bgra=1` the plugin sets `TU_DEBUG=sysmem,nocb`: every pass renders in system memory. Tile memory holds a colour
in the byte order its render target writes, so a GMEM load or store must move the bytes with the identity swap on the memory
side; the recorded Mesa patch `turnip-gmem-mutable-swap.patch` does that for resolve, 2D and 3D stores and 3D loads. With it
the lock screen matched the RGhA picture to 99.5 % in tile memory, but the GPU time per command buffer was no better than in
system memory (17.8 ms mean, 56.1 ms at p95, against 17.1 and 52.1) and one home screen frame still came out with red and blue
exchanged, so system memory stays the default. `sheng-tu-debug=` overrides it for experiments.

### Find where a slow frame goes {#frame-path}

Split a slow frame into the time each layer holds it before changing anything. Every segment below is
measured on the host uptime clock; the GPU's always-on counter is mapped to it by a fitted line.

| Segment | Where it is measured |
| --- | --- |
| Commit to scheduler | Runtime stage records (commit, prepared, handed, taken). |
| Scheduler to submit | Runtime stage records, with the reason a batch was held. |
| Submit to GPU start | Driver job timeline: the jobs ahead in the ring, by process. |
| GPU start to end | CP start and end stamps per job; Turnip stamps per render pass. |
| GPU end to handler | Driver retire time, the completion waiter, the completed handler. |

Measured on sheng with iPadOS 27 (widget page, Settings, Safari):

- Driver lock waits stay under 7 ms. A render pass takes 0.5 ms of GPU time at the median, a full-screen pass 1.1 ms.
- Most slow frames wait in the ring behind other processes' jobs: a poster extension submitted jobs of about 77 ms each,
  and the ring runs jobs in order with no priority.
- The runtime threads that bring a command buffer to its handlers ran at the default QoS: the class was set on macOS only.
- Blocks of 94 to 112 MiB took 281 to 340 ms to wire when Settings and Safari opened.

## 4. Build and stage Metal

Run these commands from the resolved target tree after preparing the matching
SDK, compiler dependencies and ABI inputs:

```sh
python3 scripts/build-turnip-darwin.py --target ios
python3 scripts/build-adreno-metal-plugin.py
python3 scripts/add-gpu-plugin-data.py --publish /path/to/base.dbr /path/to/gpu.dbr
```

The staging command uses macOS image tools and writes a copy of the Data seed.
Use that output as `--data-ramdisk` when building the payload, then rebuild the
boot image. For selected app processes, the staging command also accepts
`--clients NAME,...`. The runtime plugin name is `NativeAdrenoMetal`.

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

A pipeline compiles from Apple's AIR the first time something asks for it, which stalls frames. Warm the caches ahead so the desktop finds them. Two inputs do this, and both use the same mechanism for every OS profile (iOS/iPadOS 17 `--target ios`, 27 `--target ios27`); only the library list differs, because it names the libraries of that OS image.

1. **Priming list.** Write the absolute path of every `.metallib` of the OS image (OS and SystemOS volumes), one per line, as the render server sees it (`/System/Library/...`). Keep it in `build/prime-list.txt`; `build-adreno-metal-plugin.py` embeds it in the plugin as the `__DATA,__primelist` section, and `make-gpu-addon.py --prime-list FILE` ships it as `addons/NativeAdrenoMetal.primelist`. With a list the render server does not scan directories: its sandbox hides most of them.
2. **Pipeline pack.** Boot an image built with `make-gpu-addon.py --cache-export`; the plugin writes its cache directory to the board log. Read the run with `scripts/read-sheng-log.py`, merge one or more exports with `scripts/make-m2vpack.py OUT EXPORT_DIR...` (later directories win) and ship the result with `make-gpu-addon.py --pipeline-pack OUT`. The plugin imports the pack into the cache directory before the runtime opens it.

How priming runs:

- It starts 90 s after the render server opens the device, on a background thread with an 8 MiB stack.
- Each kernel function becomes a compute pipeline. Each vertex function becomes a render pipeline with the fragment function of the same stem (`_vert_` to `_frag_`) and one BGRA8 attachment. Pipelines made later with other constants or attachments still compile on demand.
- It waits while the desktop animates: more than 8 command buffers in 250 ms is busy, and the idle desktop at 120 Hz submits about 6. After an animation it waits 2 s of quiet, and it never waits longer than 10 s, so one pipeline still compiles on a desktop that never settles.
- Progress lives in the cache directory: `prime-done` (finished libraries), `prime-fn` (finished functions of libraries not finished yet), `prime-current` (the function being compiled), `prime-bad` (functions that ended the process; a start that finds `prime-current` moves it there) and `prime.log`. A restart resumes inside a library with thousands of functions.
- Each finished entry carries the build id: the runtime's translator build plus the Turnip library's `LC_UUID`. A runtime or Turnip rebuild primes every library again; a plugin rebuild alone keeps the work.
- The PR row of the board log shows what the thread does (compiling, waiting, opening a library), libraries done of the list, pipelines made and the highest submit rate a wait saw.

**Expected result:** the PR row reaches all libraries of the list, and a second boot shows no new pipeline compiles for the same scenes. Record the list size, the build id and the cold and warm frame timings.

## Next step

Continue with [Wi-Fi](/porting/network), or return to the
[driver checklist](/porting/drivers).
