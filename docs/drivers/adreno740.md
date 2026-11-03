# Adreno740

Adreno740 implements the A740 kernel GPU interface on SM8550. It owns GPU memory mappings, command submission, fences and CP/GMU initialization. The board supplies firmware, power votes and display integration. See the [GPU adaptation procedure](/porting/gpu).

## Runtime path

Metal → AdrenoMetal → metal2vulkan → Turnip → Darwin KMD → Adreno740 → A740.

Each client has an address space and queue range. The GPU uses 4 KiB SMMU pages. Owned buffers use system memory; imported pages retain their owners. Allocation capacity follows available memory. Mapping handles are indexed, and unmap invalidates the affected translations.

## Scheduling

| Requested priority | Ring in mode 2 |
| --- | --- |
| High (0), normal-high (4), real-time (5) | 0 |
| Normal (1), low (2), background (3), unspecified | 1 |

The task's GPU role selects its foreground or background request. Ring 0 takes precedence; ring 1 gets service when ring 0 is idle or its oldest job has waited 250 ms. An aging grant gives ring 1 a 2 ms service interval, preventing immediate switch oscillation. Switch completion immediately reevaluates queued high-priority work. Scanout observes the completed prefix across both rings. A queue stays on its existing ring until its outstanding prefix completes, preserving FIFO across priority changes. IB handles identify command storage and do not infer resource dependencies. Turnip's client queues share one kernel FIFO; unresolved syncs wait for producer submission.

Each ring tracks its queued context and page table. The CP records the executed table after `CP_SMMU_TABLE_UPDATE`, and preemption restores that snapshot. Context switching saves GMEM, runs the performance-counter SRAM postamble and holds the GMU keepalive vote until the incoming WPTR is restored. Read pointers come from each ring's own shadow. Active jobs retain their ring identity when the fence-history table wraps.

The reference enables mode 2 with `sheng-gpu-preempt=2`. Mode 1 sends only low/background requests to ring 1; mode 0 uses one ring. CPU-only page-table switching also uses ring 0. The switch watchdog is 1 s. A failed switch disables further preemption and recovery replays pending work on ring 0; diagnostics retain the failure.

## Build and verification

From the resolved iOS 27 target tree, with `UNIXNU_XNU_ARCH=arm64e` and `UNIXNU_IOS_VERSION=27.0`:

```sh
python3 scripts/build-arm-driver.py Adreno740
python3 scripts/build-adreno740-kits.py
python3 scripts/check-native-adreno-scheduling.py
```

The host scheduling check runs the real ring, preemption and submit code over software register peers with address and undefined-behavior sanitizers. It checks packets, GMEM and keepalive sequencing, timeout handling, page-table snapshots, priority routing, FIFO and fence-history rollover. Hardware qualification requires concurrent clients, repeated ring switches, correct pixels and frame-pacing measurements.

See [AdrenoMetal](/drivers/adreno-metal) for Metal interfaces, caches and plugin staging.

Frame diagnostics retain allocation, command, completion and GPU/display timing. Pixel capture is disabled. See [GPU frame diagnostics](/porting/gpu-diagnostics).
