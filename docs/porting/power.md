# DSP, audio and power drivers

Complete [platform memory, interrupts and DMA](/porting/platform) first.
Implement the transport, device protocol and OS service as separate parts.
Use the source references below for the matching hardware and firmware interface.
Each step produces a specific interface or observable result.

## 1. Identify the target interfaces

Collect these inputs from the target DTS, firmware source and vendor driver:

| Function | Inputs | Implementation output |
| --- | --- | --- |
| DSP | Firmware/PAS IDs, memory reservations, mailbox interrupts, shared-memory layout, clock and power ownership | Firmware loader and message transport |
| Audio | Codec/amplifier IDs, buses, clocks, routes, DSP topology, supported formats and OS audio ABI | Endpoint configuration, stream engine and OS service |
| Battery | Gauge or firmware protocol, property IDs, units, current sign and notification messages | Measurement decoder and power-source service |
| Power | Clock domains, OPP tables, regulators, firmware votes and thermal limits | Board policy using the appropriate controller interfaces |

Use [firmware inventory](/porting/device-repository) to record each binary's source
and version. A board with a direct I2C gauge implements that gauge's register
protocol; a board using a DSP battery manager implements its message protocol.
Choose the transport before selecting the reference code.

## 2. Implement the DSP transport {#dsp}

| Source | Implementation to inspect |
| --- | --- |
| [AdspProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/AdspProbe.cpp) | Firmware loading, SMEM, SMP2P, GLINK, mailbox and resource setup |
| [ShengAdsp.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengAdsp.h#L15) | `ShengAdspClient`, channel registration and queued sends |
| [LegacyDisplayProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/LegacyDisplayProbe.cpp#L493) | Initialization order for DSP and its consumers |

The linked files illustrate a Qualcomm GLINK integration. For that interface:

1. Adapt firmware authentication, reserved memory and power votes to the target.
   Establish the mailbox and ready/crash notification paths before opening a channel.
2. Implement the channel state and receive callbacks from `ShengAdspClient`.
   They run on the DSP thread: copy received bytes into a bounded queue and wake
   the consumer's work loop. Keep request processing and waits on the consumer.
3. Register the target channel with `sheng_adsp_channel(name, intent_size,
   intent_count, initiator, callbacks, context)`. Get the name, receive-buffer
   sizes and opening direction from the target service protocol.
4. Handle `sheng_adsp_send` results: `0` queues the message, `-1` reports a full
   queue or oversized message, and `-2` reports invalid arguments. The reference
   API accepts messages up to `SHENG_ADSP_MAX_MESSAGE` (512 bytes). A service with
   larger packets needs corresponding transport and receive-buffer support.
5. On disconnect, cancel requests and invalidate remote handles. On reconnect,
   negotiate the channel and restore subscriptions before resuming consumers.

**Result:** a channel opens, exchanges a bounded request/response, reports a
failure and reconnects. Record the channel name and response bytes with
[log capture](/porting/log-capture).

## 3. Implement audio streams {#audio}

For Qualcomm AudioReach/GPR firmware, use these references in execution order:

| Source | Purpose |
| --- | --- |
| [ShengGpr.h](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/ShengGpr.h), [ShengAudioReach.h](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/ShengAudioReach.h) | Packet headers, APM readiness, graph open and configuration, memory map, PRM votes and clocks |
| [AudioProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/AudioProbe.cpp), [ShengCs35l43.c](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/ShengCs35l43.c) | Amplifier setup over I2C, graph bring-up, period buffer flow, codec SoundWire start, microphone capture |
| [ShengAudioService.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/ShengAudioService.cpp), [ShengAudioPlugIn.c](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/hal/ShengAudioPlugIn.c) | Audio service for the OS audio server and its plug-in |
| [Linux q6apm.h](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/q6apm.h), [q6apm.c](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/q6apm.c) | Graph lifecycle, memory mapping and read/write requests |
| [Linux audioreach.c](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/audioreach.c), [topology.c](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/topology.c) | Module configuration, graph connections, media formats and endpoint parameters |
| [Linux q6apm-dai.c](https://github.com/torvalds/linux/blob/v6.12/sound/soc/qcom/qdsp6/q6apm-dai.c) | `q6apm_dai_prepare`, stream events and period-buffer flow |

Linux supplies protocol and stream-lifecycle references. Implement their
allocation, scheduling, DMA and completion operations using the selected XNU
interfaces, and retain the applicable source licenses when reusing code.

1. **Open and identify the service.** Verify the target firmware's GPR domains,
   ports, packet size and opcodes. Match replies to request tokens. Use the
   readiness exchange as the first protocol check.
2. **Describe one complete route.** Record graph/subgraph IDs, module instance IDs,
   connections, codec port, amplifier setup, clocks and channel map for one
   playback or capture endpoint. Obtain these from the target firmware topology
   and codec driver. Implement that route's register operations and power order.
3. **Implement graph commands.** Add open, configure, prepare, start, stop and
   close operations following `q6apm_graph_*`. Check every response and keep the
   graph ID and state with its owning stream. Release successfully created
   objects when a later operation fails.
4. **Implement the buffer path.** Allocate DSP-accessible period buffers, map
   them through the firmware protocol, set PCM format and channel mapping, then
   prepare/start the graph. Queue playback through the equivalent of
   `q6apm_write_async`; queue capture buffers through `q6apm_read`. On completion,
   synchronize caches, advance the stream position and reuse the completed buffer.
   Stop outstanding work before unmapping and closing the graph.
5. **Connect the OS service.** Identify the target OS audio provider, required
   methods, request layouts, mapped-memory types and completion notifications
   from the selected kernelcache and framework. Record these ABI inputs using
   [built-in driver integration](/drivers/xnu-drivers#compile-against-the-kernel-abi).
   Connect format selection, start/stop, position and buffer completion to the
   stream engine. Publish only formats and routes implemented by that endpoint.
6. **Exercise the route.** Play a known PCM signal or record a known input. Check
   channel order, rate, position and buffer contents. Repeat start/stop and test
   buffer starvation, timeout and DSP restart. Verify OS application playback
   or recording after the direct stream path succeeds.

On SM8550 these firmware details decide whether a route starts:

- The DSP takes a buffer as a 32-bit address with the stream index (`0x1001 & 0xf`) in the upper word. Place the period buffer below 4 GiB.
- The DSP offers small GLINK intents first and grants a larger one on request. Keep the granted intent even when the remote intent table is full.
- PRM requests use the PRM's own port and PRM clock IDs; the TX core clock is `0x30c`, not the device tree index.
- The VA macro gates the TX SoundWire master clock as well as the TX macro.
- CoreAudio assumes a 24 MHz host clock. On a 19.2 MHz timebase the audio service corrects CoreAudio's constant at start, otherwise the audio server's IO cycles run 25 percent long and playback and capture stutter.

**Result:** a complete route carries PCM data, reports progress and releases its
resources. Save the route description, format, stream counters and captured
output. The next endpoint gets its own route configuration and observations.

### Microphone capture {#microphone}

A capture route adds a codec and a SoundWire link to the stream steps above.

1. **Power the codec.** Release its reset and enable its supply. Vote the TX and
   VA macro clocks, then open both gates: on SM8550 the VA macro also gates the
   TX SoundWire master.
2. **Bring up the SoundWire link.** Start the TX master and wait for the codec to
   enumerate. Read its manufacturer and part IDs before configuring it.
3. **Configure the analog path.** Select the microphone input, its bias and the
   ADC, set the ADC gain, then map the ADC to a codec data port and channel.
4. **Configure the digital path.** Connect the master port to the TX decimator
   that reads it, and the decimator to the codec DMA interface the DSP graph uses.
5. **Read buffers.** Queue capture buffers through the read request. Each answer
   carries a byte count and an offset; take only those bytes, a short period is normal.
6. **Publish the input.** Expose an input stream only after a direct capture of a
   known sound succeeds.

The reference route, from [AudioProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/main/package/AudioProbe.cpp):

| Stage | Reference value |
| --- | --- |
| Codec | WCD938x, reset gpio108, supply ldob15, SoundWire device 1 on the TX master (0x6d30000) |
| Analog | AMIC3, micbias 3, ADC2 |
| Link | Codec data port 1 channel 2 to master port 2 |
| Digital | TX decimator 0 from SWR_MIC1, codec DMA TX3 |
| Format | Mono, 48 kHz |
| iOS | The HAL plug-in's input port; iOS accepts it with the Thunderbolt transport type |

Check capture with `sheng-audio=4`, which reads two seconds at boot: the
`[mic]` and `[mic capture]` log rows give returned periods, bytes, the share of
non-zero samples and the peak. Then record in an app and read `[audio-io]`.

## 4. Implement battery reporting {#battery}

| Source | Purpose |
| --- | --- |
| [ShengBattmgr.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengBattmgr.h#L30), [ShengBattmgr.c](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengBattmgr.c) | Request/response format, refresh state machine and unit conversion |
| [ShengBattery.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengBattery.cpp#L39) | `IOPMPowerSource` properties, work loop, timers and notification handling |
| [BatteryProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/BatteryProbe.cpp#L16) | Class registration and service startup |
| [XNU IOPMPowerSource.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-10063.141.1/iokit/IOKit/pwr_mgt/IOPMPowerSource.h) | Power-source setters and status publication API; match the selected XNU version |
| [Linux qcom_battmgr.c](https://github.com/torvalds/linux/blob/v6.12/drivers/power/supply/qcom_battmgr.c) | Qualcomm battery-manager protocol variants and property handling |

1. Implement the target gauge read or firmware request. For the referenced PMIC
   GLINK protocol, match owner, message type, opcode, property ID and response
   length before consuming a value. Keep one request outstanding and handle its
   timeout before advancing the refresh cycle.
2. Store valid readings separately from absent or failed values. Implement a
   snapshot with presence, external power, charge state, capacity, voltage,
   current, temperature and time remaining. Document each raw-to-OS conversion.
   The reference maps voltage/current from micro-units to milli-units, capacity
   from hundredths of a percent, and remaining time from seconds to minutes.
   Confirm the target's units and charging-current sign before using those mappings.
3. Subclass `IOPMPowerSource` using the selected XNU headers. Create a work loop,
   response queue and request/refresh timers. Feed received messages to the
   decoder; update properties from a completed snapshot.
4. Publish the initial valid properties with `registerService()`, then notify
   changes with `updateStatus()`. Set installed, external-power and charging
   state consistently with capacity and measurements. Adapt adapter details to
   the target OS property definitions.
5. Subscribe to change notifications and schedule periodic refresh. On transport
   loss, cancel pending requests and mark readings stale in the driver; apply
   the selected OS policy for unavailable data until refresh succeeds.
6. Compare raw readings and published properties against the target's gauge or
   stock-system readings. Exercise connect/disconnect, charging/discharging,
   response timeout and service restart. Check OS-visible updates separately
   from protocol responses.

**Result:** the OS receives measurements with documented units and timely updates.
If the firmware owns charging control, retain that ownership while implementing
measurement publication. A host-controlled charger needs its own controller
protocol, limits and thermal policy.

## 5. Implement frequency and power operations {#power}

Read [CpuFreqProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/CpuFreqProbe.cpp) for EPSS LUT and CPU/L3 operating-point access, [QcomRpmh.h](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/QcomRpmh.h) for resource
votes, and [ShengPlatformPower.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/ShengPlatformPower.cpp) for the OS-facing platform-power integration.
These are references for the corresponding Qualcomm hardware interfaces.
[GpuPowerProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/552b67499135bae191f415f444d782a6942c252e/package/GpuPowerProbe.cpp) holds the GPU clock governor.

1. Match CPU affinities to performance domains. Read the target's LUT entries,
   reference clocks and enabled state; convert entries into rates using that
   controller's encoding.
2. Implement an operating-point request and status readback. Apply the target's
   regulator, interconnect and thermal requirements in the documented order.
3. Define ownership and reference counting for peripheral power votes. Release
   resources after dependent DMA and interrupts are stopped.
4. Connect the selected OS power callbacks. For suspend/resume, save the required
   state, restore clocks and mappings, rearm interrupts and resume consumers.
5. Measure frequency under load, then verify each peripheral transition and
   resume path with its dependent drivers active.

On SM8550 the governors use these inputs:

- CPU: each CPU's idle time from the scheduler, read every 16 ms. A domain follows its busiest CPU with a 1.25 margin and steps down after four quieter windows.
- GPU: the GMU XO busy counter. The level that keeps the GPU about half busy is voted over HFI together with that level's bandwidth.
- Touch: a touch report holds the P CPU domains and the GPU at their top level until 1 s after the last report (`sheng-cpufreq-boost-ms`, `sheng-gpu-dcvs-boost-ms`).
- Frames: GPU submissions in 2 of the last 4 windows keep every CPU domain at 60 percent of its top level or more for 300 ms. GPU work after an idle drop starts at twice the current clock, at least 578 MHz, for 50 ms.
- Fence waits: a waiter sleeps until the fence interrupt, at most 1 ms (`sheng-gpu-pause-us`), instead of polling.

**Result:** frequency requests and power transitions have observed effects and
preserve the dependent devices' operation.

## 6. Build and verify the interfaces

Follow [driver build integration](/porting/drivers#build-integration) to add the
sources, ABI bindings, initialization caller and archive inputs. The reference
[build-gop-legacy-display.py](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/scripts/build-gop-legacy-display.py#L253) shows how the DSP, battery service and audio probe are compiled; [LegacyDisplayProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/LegacyDisplayProbe.cpp#L493)
shows their call order. Choose initialization points that satisfy the target's
platform, transport and OS dependencies.

From the main checkout with the target selected:

```sh
./unixnu status --json
./unixnu kernel
./unixnu payload
./unixnu bootimg
```

Before building, prepare the selected OS and [local inputs](/reference/configuration#local-build-inputs).
Use the target's documented enable arguments. Record protocol replies, graph or
service publication, data flow and restart behavior in its [porting record](/porting/records).
Continue with [bring-up](/porting/bring-up).
