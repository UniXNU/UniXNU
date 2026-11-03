# Display and brightness

Start after [platform and memory](/porting/platform). Collect the firmware GOP
base, size, dimensions, stride, pixel format and reserved-memory range. Identify
the panel, display controller, backlight controller and their power owners.

Use [driver build integration](/porting/drivers#build-integration) to connect
initialization, archive recipes and the OS ABI, then run this page's hardware checks.

## Sources and interfaces {#source-map}

These links identify reviewed source revisions. Match interfaces to the selected
SoC, component and OS versions. The linked device sources provide board integration
examples.

| Implementation | Source | What to read and implement |
| --- | --- | --- |
| OS display interface | [NativeLegacyDisplay.cpp](https://github.com/UniXNU/GopFramebuffer/blob/cf3b42979a9c44219e7bb149543e6fc3388b58ed/NativeLegacyDisplay.cpp), [OriginalMobileFramebufferABI.h](https://github.com/UniXNU/GopFramebuffer/blob/cf3b42979a9c44219e7bb149543e6fc3388b58ed/OriginalMobileFramebufferABI.h) | Provider methods, request layouts and selected MobileFramebuffer ABI |
| Frame ownership | [NativeGOPWire.h](https://github.com/UniXNU/GopFramebuffer/blob/cf3b42979a9c44219e7bb149543e6fc3388b58ed/NativeGOPWire.h#L6), [NativeGOPPresenter.cpp](https://github.com/UniXNU/GopFramebuffer/blob/cf3b42979a9c44219e7bb149543e6fc3388b58ed/NativeGOPPresenter.cpp) | `NGPPresent`, `NGPSwap`, `NGPComplete`: buffer bounds and swap retirement |
| Brightness implementation | [AppleARMBacklight.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/AppleARMBacklight.cpp), [GeniI2c.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/GeniI2c.h#L80) | OS properties and `geni_i2c_start_write/read`, event and timeout handling |
| Timing reference | [DisplayTimingProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/DisplayTimingProbe.cpp) | Target controller counters and refresh measurement |

## 1. Establish firmware scanout

Build the [integrated UEFI firmware](/porting/uefi-firmware). Confirm that its
menu displays correctly. Compare GOP geometry and framebuffer bounds with the
firmware memory map and board DTS. Preserve the active scanout allocation through
kernel handoff.

**Expected result:** a stable firmware image with correct colors and dimensions.
Resolve this before enabling the XNU presentation backend.

## 2. Adapt the XNU display backend

Read [GopFramebuffer](/drivers/gop-framebuffer) and its `NativeLegacyDisplay.cpp`,
`NativeGOPPresenter.cpp` and `NativeGOPWire.h`. It consumes `PE_current_console`
and integrates with the selected MobileFramebuffer and IOSurface ABI.

In the [reference board package](https://github.com/UniXNU/UniXNU-sheng/tree/main/package),
inspect `LegacyDisplayProbe.cpp` and `DisplayTimingProbe.cpp`. The device's
`scripts/build-gop-legacy-display.py` qualifies ABI methods against a prelinked
candidate before producing the late display archive. Supply the matching
candidate and audit inputs listed in [build inputs](/porting/migration#build-inputs).

1. Select GopFramebuffer and the display archive recipe, preserving its dependencies.
2. Enable the recipe's kernel configuration and initialization caller. The reference uses
   `CONFIG_XNU_NATIVE_LEGACY_DISPLAY=y` and its `offline-legacy-*` arguments.
3. Check pixel layout, row stride, allocation size and cache handling in CPU
   presentation. Confirm that a known frame reaches the display.
4. Check swap completion and IOSurface lifetime before enabling
   [GPU presentation](/porting/gpu).
5. Adapt timing reads to the target display controller. The reference probe, `sheng-dpu=1`,
   samples the SM8550 DPU and dual-DSI counters through `DisplayTimingProbe.cpp`.
   Set refresh policy from the observed panel mode. The reference requests 120 Hz with `sheng-vsync=120`.

For the `NativeGOPWire.h` path, query mode/geometry first and validate each
present buffer's size and stride. In GPU handoff, track the pending frame by
`NGPSwap.sequence` and return `NGPComplete` with that sequence after copying.
Retain the source frame and IOSurface until the swap completes, and complete
the corresponding error path on timeout or failure.

**Expected result:** XNU publishes the display, presents frames and completes
swaps. Record requested refresh and measured frame timing separately.

The 24A446 adapter supplies the default surface through the original IOSurfaceRoot
factory and validates its backing memory and geometry before transferring ownership
to the display family. The family's `create_default_fb_surface()` slot returns void;
its residual return register is not an object pointer. A captured 300-second boot
completed three swaps without a kernel panic and displayed the Apple logo.
Home-screen startup remains unverified; capture the display-server and SpringBoard
wait chains before treating a stationary logo as a framebuffer transfer failure.

### Read the display pipes {#dpu-pipes}

Before changing what the display fetches, read how firmware left it.
The reference `DisplayTimingProbe.cpp` exposes these stages:

| Argument | Reads |
| --- | --- |
| `sheng-dpu=2` | VIG 0 and 1 source, size, format and fetch settings; CTL 0 state; the tear check of both interfaces; the display streams in the apps SMMU |
| `sheng-dpu=3` | Also rewrites each pipe's current address and times the CTL flush latch |

In this reference, both VIG pipes fetch one 32-bit physical address, the right pipe from
its own source x, and a flush latches within 5.4 ms without a start because the
panel refreshes by itself. The display context bank starts with translation off.

Direct scanout (`sheng-dpu-scanout=2`) is experimental and off by default: it
gives the display bank a stage 1 window (ShengUfs) and points the pipes at the
compositor's surfaces. Any failure falls back to the GPU copy.

The window's TCR2 sets the sign extension field (SEP, bits 17:15) to 7, as
arm-smmu does for AArch64 contexts; with SEP 0 an address with bit 31 set faults
at level 0. The compositor submits a swap when its command buffer is scheduled,
not when the GPU finished it, so the display driver flips only after the GPU
wrote everything handed to it before the swap arrived (the Adreno driver exports
the newest and the completed fence). Without that wait the pipes scan a surface
the GPU is still writing and the panel flickers. The boot log row
`[direct scanout]` shows flips, mapped surfaces, latch times and the time the
flips waited for the GPU. The framebuffer must be 8-bit BGRA.

## 3. Identify the brightness transport

Select the target's I2C, DSI-command or PWM transport and its brightness encoding.
`AppleARMBacklight.cpp` provides an OS-service example for KTZ8866 controllers;
`GeniI2c.h` defines the GENI transfer state machine used by that example.

Before reuse, record the target's controller count, register encoding, brightness
range, I2C engine, slave address, pins, clocks, interrupts and power sequence.
For a DSI-command or PWM backlight, implement that transport and its level encoding
behind the OS-facing brightness service.

## 4. Adapt and enable brightness

1. Update the board's engine mappings, clock votes and interrupt routing.
   The reference GENI path adopts firmware-loaded engine code and timing; verify that
   handoff or implement the target's initialization sequence.
2. Implement the target controller's level encoding, write and readback. Match
   the number of controllers and update order to the panel's wiring.
3. For the GENI example, call `geni_i2c_prepare`, start a read/write, feed interrupt
   status to `geni_i2c_event` and call `geni_i2c_timeout` when its deadline expires.
   Complete or cancel the transfer before starting the next one. Keep service
   requests on the work loop and inspect failures before enabling fades.
4. Match `IODisplayParameters` brightness limits and `backlight-control` to the
   selected OS ABI. The service accepts brightness and `FadePeriod` properties.
5. Build the service and its registration wrapper. The reference display recipe does
   both; `sheng-backlight=1` enables its probe.

From the resolved target tree, locate these integration points:

```sh
rg -n 'kSeA|kSeB|kSpi|kMaxLevel|backlight-control|FadePeriod' kits/*/AppleARMBacklight.cpp
rg -n 'backlight|GeniI2c' scripts/build-gop-legacy-display.py
```

Use the equivalent kit path for the new board. Rebuild the kernel, payload and
boot image through [Building](/building).

**Expected result:** minimum, middle and maximum settings produce corresponding
readback and visible levels; fades complete; timeout counters remain stable.
The reference `native_backlight_stats` records publication, requests, readback,
interrupts and failures. Verify UI brightness changes as a separate step from
raw controller writes.

## Next step

Record display and brightness results separately, then continue with
[touch and buttons](/porting/input).
