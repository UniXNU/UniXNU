# AdrenoMetal

AdrenoMetal publishes a Metal device through `MTLAddDevice`. It translates AIR through metal2vulkan, compiles SPIR-V with Turnip, and submits work to [Adreno740](/drivers/adreno740). Firmware, power votes and display integration come from the board.

## Rendering and interfaces

| Area | Behavior |
| --- | --- |
| MSAA policy | All clients use one sample for textures, pipelines and render passes by default. Resolve targets receive the rendered output; load and store-and-resolve preserve the source. `NATIVE_METAL_SINGLE_SAMPLE=0` preserves a process's requested sample counts; `1` forces single-sample rendering. |
| Heap resources | Buffer and texture `makeAliasable` release their heap ranges. |
| Texture layout | Creation, heap size queries and texture views retain the caller's `allowGPUOptimizedContents` setting. |
| Texture channels | Texture descriptors and views preserve all four swizzles, including explicit zero and one. |
| Copies and raster state | Blits cover the requested mip and slice ranges. Viewport and scissor setters forward every entry, up to 16. |
| Compressed input | A zero-length no-copy compressed texture infers its DroidVM layout size and retains the owner's deallocator through use. |
| Source compilation | `mathMode` selects safe, relaxed or fast arithmetic. `mathFloatingPointFunctions` independently selects fast or precise FP32 functions. Older option objects use `fastMathEnabled`. |
| Functions | Function constant dictionaries expose names, indices and types. Function and compute-pipeline completion selectors report results. `specializedName` is the exported name; source lookup retains the original definition. |
| Constant tables | Dynamically indexed constant tables larger than 4 KiB use shared constant storage. Constant pointer casts and GEP expressions retain their offsets. |
| Memory accounting | Device allocation totals include pooled, dedicated and imported backing. Texture sizes come from their backing allocation. The recommended working set is RAM / 4, capped at 2 GiB. |
| Queue capacity | `newCommandQueueWithMaxCommandBufferCount:` uses the runtime's outstanding-buffer limit. Uncommitted destruction releases a slot; completion releases it after handlers return. |

A render pass that fails encoding returns an encoder and reports a command-buffer error. This supports callers that cache encoder methods.


Unused owned image backing is reused by pooled and dedicated images. Extra spares have no byte limit, expire after ten seconds, and go sooner under memory pressure or when a new block cannot be made. Blocks are freed off the releasing thread on the runtime's free thread, and on the releasing thread once its queue is full. An allocation failure releases kept spares and waits for posted frees before retrying. Imported memory and owner callbacks keep their release ordering. First-use allocations can still prepare new pages.

## Native half arithmetic

On A740, half FMA uses float32 multiply-add followed by conversion to half, with a one-half-ULP bound for normal half operands and results. Half division scales both operands by the same power of two to keep the native divisor in `[2^-14, 2^14]`: large divisors use `2^-2`, small divisors use `2^10`. Normal operands and results follow Vulkan's 2.5-half-ULP bound; the device's float controls determine denormal behavior.

Other eligible half operations use `RelaxedPrecision` with `HalfChainPolicy::AtExits`. The source-derived arithmetic inventory records each operation's `PrecisionNote`; the runtime policy log records the selected device capabilities.

## Cache and priority

Clients with the same UID use `Library/Caches/org.unixnu.metal` under their account home when writable. Sandbox restrictions select a private cache. `NATIVE_METAL_SHARED_CACHE_DIR` selects another shared root; an empty value disables sharing. The cache covers Apple frontend output, runtime artifacts and Turnip IR3. Concurrent pack imports use distinct temporary files. Pipeline journals are per process.

`metal-flow=<bits>` selects render work placement. Bit 1 uses the lowering worker and bit 2 submits directly from commit; macOS defaults to 3. iPadOS also supports bit 4 for warming earlier pipeline records and defaults to 7.

Any value of `metal-flow=` logs the `FL` counts to os_log every ten seconds when they change.

Turnip chooses tile memory or system memory for each render pass, and concurrent binning is on. `tu-debug=<flags>` sets `TU_DEBUG` for every Metal process: `gmem` renders every pass in tile memory and `nocb` turns concurrent binning off. `tum=a` alternates between Turnip's choice and tile memory every eight seconds for measurement.

Logical Metal queues share one Vulkan queue and kernel queue per process. The frontend forwards the most urgent **current** request among live queues. Lowering or destroying a queue removes its boost. Getters report each queue's own request; setters report backend acceptance. The kernel chooses foreground or background priority from the task's GPU role. Priority policy does not use process names.

## Shader priming and diagnostics

Source and packaging: [AdrenoMetal](https://github.com/UniXNU/AdrenoMetal/pull/38), [UniXNU](https://github.com/UniXNU/UniXNU/pull/271), [sheng](https://github.com/UniXNU/UniXNU-sheng/pull/107).

On macOS, open **Shader Cache** and click **Start** to compile the system inventory. The window shows library progress, compiled functions, failures and missing inputs. **Stop** finishes the current compilation before stopping. Starting again keeps successful checkpoints and retries failed entries. Administrator authorization gives the worker access to the shared system cache. Closing the window keeps the requested task running.

The app is installed at `/Library/GPUBundles/Shader Cache.app`; the sheng lab exposes it in `/Applications`. Build it with the macOS plugin:

```sh
python3 scripts/build-adreno-metal-plugin.py --target macos27 --no-replay
```

The runtime build inventories `.metallib` files from OS, SystemOS and App. The worker uses reflected constants and vertex inputs for default compute pipelines and BGRA8/RGBA16Float render variants. Apple GPU machine-code archives are counted separately. A library enters `prime-done` after all selected variants compile. Missing inputs and refused variants produce an incomplete result.

The worker stores status in `shader-cache.plist`, its active-task lock in `shader-cache.lock`, and checkpoints beside `prime.log` under `/private/var/tmp/NativeAdrenoMetal.cache`. Checkpoints retain the translator and Turnip identity. All Metal clients read the shared cache through `/Library/GPUBundles/NativeAdrenoMetal.cache`.

Read status or summarize a captured cache:

```sh
'/Applications/Shader Cache.app/Contents/MacOS/ShaderCache' --status
python3 scripts/analyze-metal-prime.py CAPTURED_CACHE_DIRECTORY
```

On iPadOS, the render server compiles the inventory while idle and reports progress through `PR`, `PRb` and `PRc`.

`FP` reports grouped submissions and batches, command pools made and reused, linear passes rendered in place and through copies, and region pipelines evicted. `CM` reports commit calls and cumulative microseconds in total, lowering, recording, pipeline waits, lock waits, scheduler passes and submission. Compare counter differences within the same controlled workload.

With `diag=1` or `gpu-trace=1`, the system cache also holds bounded `timing.log` (512 KiB) and `runtime-policy.log` (64 KiB). The timing log contains per-encoder timings and command buffers taking at least 8 ms. The policy log records the actual device policy, float controls and runtime path checks. Both files are included in sheng's diagnostic export.

Imported surfaces and padded textures take the runtime's in-place route after its device check accepts the layout and usage. The runtime selects submission grouping and queue sharing from the device's supported capabilities and its submission checks. Idle resource cleanup waits for the next expiration deadline.

## Performance acceptance

Use a fixed scene, display mode, battery range and temperature range. Record the source revisions and window state with the capture. The performance target has these checks:

| Area | Target |
| --- | --- |
| Shader coverage | This boot's whole-system pass reports complete, with every eligible library finished and no failed or missing entry. The warmed scene adds no compilation misses. |
| Fast paths | Every policy field has a recorded device-capability decision. Supported native approximate operations retain their required precision semantics. |
| Frame cadence | During continuous animation, the 99th-percentile display interval fits one scan period, allowing timestamp resolution. At 120 Hz the period is 8.333 ms. |
| Scheduling | GPU-ready work has at most 0.25 ms of avoidable scheduling delay at the 99th percentile. Every larger interval has a trace identifying its dependency or bottleneck. |
| Hardware throughput | Isolated arithmetic and bandwidth probes reach at least 95 percent of the same device's calibrated native throughput with matching formats, precision, clocks and temperature. |
| Correctness | The scene completes with matching output, no GPU faults or recovery, and no client crashes. |

Compare CPU and GPU durations within their own clock domains. Calibrate timestamps before combining them. Retain the capture for each unmet target and use it to select the next change.

## Build and checks

From the resolved iOS 27 target tree:

```sh
python3 scripts/build-turnip-darwin.py --target ios27
python3 scripts/build-adreno-metal-plugin.py --target ios27
python3 scripts/check-native-metal-frontend-host.py
```

`NMB_PREBUILT_BRIDGE` selects a bridge archive metadata file. The builder checks its target, translator tree, component, wrapper, fixtures, manifest and archive digest against the selected sources before reuse. Source builds retain a two-hour Cargo budget. `python3 scripts/package-metal-bridge.py OUTPUT.tar.zst --target macos27` packages the current archive, its identity and tracked component sources for CI reuse.

The normal build applies the recorded translator and Turnip patches and enables Mesa's disk shader cache. Host checks cover rendered pixels, resolves, resource aliasing, swizzles, copies, callbacks, queue limits and priority aggregation. Hardware qualification covers frame pacing and preemption under concurrent clients.

See the [GPU adaptation procedure](/porting/gpu) for staging and board inputs.

Frame diagnostics retain allocation, command, completion and GPU/display timing. Pixel capture is disabled. See [GPU frame diagnostics](/porting/gpu-diagnostics).

With `gpu-trace=1`, kernel event 65 identifies the Metal device and command queue used by `iconservicesagent`. Up to eight `metal-work` records report completion status, draw count and dispatch count for command buffers with GPU work.

`wallpaper-freeze=1` isolates wallpaper rendering. A Poster renderer retains its first successfully drawn and stored IOSurface output of at least two million pixels, then parks later command buffers before runtime submission. Parked buffers remain committed and unscheduled; their owners and queue leases stay retained. Previously submitted work completes normally. PosterBoard, backboardd and other clients continue submitting. The mode defaults to off.

Detailed latency records identify slow encoder calls, callback invoke addresses and resource destruction. Kernel sampling of the render, encode and completion threads correlates upstream waits.

With `diag=1`, encoding batch end records (type 14, phase 3) store encoding-thread CPU microseconds in field `d`. Compare this with paired start/end wall time to distinguish work from waits. `TUC` reports Turnip BO cache lookups, hits, inserts, evictions and full flushes.
