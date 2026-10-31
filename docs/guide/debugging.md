# Debugging and logs

Collect firmware logs, kernel output, diagnostic screenshots and build reports for each bring-up checkpoint.

## Procedure {#procedure}

1. Record the command that failed or the last completed [boot checkpoint](/porting/bring-up), plus the device, firmware and image revisions.
2. Choose an available [log source](#log-sources). Use the USB terminal only with a board that implements its [device protocol](#device-compatibility); use UART, framebuffer diagnostics or QEMU logs as provided by the target.
3. For a green handoff bar, follow [the entry-probe procedure](#green-bar). For a panic, capture the [panic screen](#panic-screen); for a user process fault, collect [user fault evidence](#user-fault-evidence).
4. Apply one diagnostic change. Rebuild the affected artifact; boot-argument changes require `./unixnu payload` and `./unixnu bootimg`. Repeat the failing operation and record the last confirmed checkpoint.
5. Save an [evidence bundle](#evidence-bundle) and update the affected [porting record](/porting/records). A useful result identifies the failing stage, input versions and exact error.

## Capture by boot stage

Follow [log capture and automated tests](/porting/log-capture): QR export from
the firmware menu, UART or screen diagnostics at kernel entry, then persistent
logs and automated cycles after storage works.

## USB debug terminal

The host tools from the giulia port are available as `scripts/debug_terminal.py` and the Windows CMD launcher `scripts/debug-terminal.cmd`. They capture CDC logs, queue bounded diagnostic commands, export topic logs and decode GSC1 framebuffer packets. Python 3.10 or newer is required. Interactive editing and PTY keyboard input require Windows CMD; scripted capture works on Windows, Linux and macOS.

```sh
python -m pip install -r scripts/terminal-requirements.txt
python scripts/debug_terminal.py --list
python scripts/debug_terminal.py --port COM21 --command collect --seconds 20
# Linux example (use the device's actual port):
python3 scripts/debug_terminal.py --port /dev/ttyACM0 --command status --seconds 5
```

On Windows, run `scripts\debug-terminal.cmd --port COM21` for an interactive session. Use `:help` for the command list. Select a port explicitly, or supply all three identity options: `--vid 0x1209 --pid 0x0001 --usb-serial ACE5DBG001` for the giulia development device. The tool refuses missing or ambiguous automatic selection. It uses 115200 baud and asserts DTR; close other port owners first.

| Command | Result |
| --- | --- |
| `all` / `collect` | Queue bounded queries; `collect` also requests replay/sample and saves after at least 15 seconds |
| `logs wifi` / `logs gpu` / `logs panic` | Filter retained session text, not fresh hardware measurements |
| `save` | Export topic text and session metadata |
| `watch status 2` / `unwatch` | Poll a read-only status query / stop polling |
| `screen.start` / `screen.stop` | Open a localhost viewer / stop framebuffer transfer |
| `screen.snapshot` | Save an actual framebuffer PNG when supplied by the device |
| `shell` | Enter the device PTY; Ctrl+] returns to diagnostics |
| `reboot.fastboot` | Request a device-side synchronized reset |

Sessions are written under `out/terminal/<timestamp>/`: rotated `device-*.log` files, topic text, `session.json` and separate screen images. Topic exports retain the latest 20,000 complete lines. Screen packets are separated from the text log. The viewer keeps the last real frame and checks device input capabilities before enabling optional mouse/keyboard controls.

```sh
python scripts/debug_terminal.py --port COM21 --command screen.start --seconds 60 --max-size 695 --max-fps 1
python scripts/debug_terminal.py --port COM21 --command reboot.fastboot --fastboot-serial DEVICE_SERIAL --seconds 20
```

Fastboot verification requires `fastboot` on PATH and matches the exact requested serial number after the kernel reset acknowledgement and CDC disconnect.

### Device compatibility

These are host tools, not a kernel upgrade. The initial backend implements the giulia protocol 2 command set, `GIULIA` shell/input/reset markers and GSC1 screen framing (up to 1264 × 2780 RGB565 pixels). Other boards must implement that protocol or add a corresponding backend. Changing USB IDs alone does not provide protocol compatibility. Board drivers, addresses, boot arguments and daemon installation stay in the device repository; see the [giulia terminal implementation and setup](https://github.com/tycykp/UniXNU-OnePlus-Ace5/blob/main/docs/USB_TERMINAL.md).

Basic kernels may only support `help`, `ping`, `status` and `replay`; extended queries require the matching terminal implementation. Screen capture requires a framebuffer producer, and remote input requires the device HID provider. PTY shell requires the development boot argument and staged daemon/shell; it has not been validated on hardware. MMIO commands retain the giulia backend's low peripheral aperture and explicit development gates; consult the device documentation for clocks, mappings and supported operations. GPU/HFI commands require the corresponding development kernel. Unsupported commands are reported by the device, and host installation does not enable them.

The imported code originates from `UniXNU-OnePlus-Ace5` at `694b39e` plus local terminal/screen changes. Host verification:

```sh
python -m unittest discover -s tests/terminal -v
```

The optional C-sender interoperability test needs `GIULIA_SCREEN_FIXTURE` pointing to the output of the device repository's screen test runner. Default tests use synthetic packets and mocked serial sessions; they do not establish hardware readiness.

## Log sources

| Source | Transport | Use |
| --- | --- | --- |
| [Firmware log export](/porting/log-capture#qr-logs) | OneSend QR frames | Current UEFI Advanced Logger buffer |
| [Persistent logs](/porting/log-capture#persistent-logs) | Reserved storage, Linux reader or recovery reader | Kernel messages and diagnostic snapshots |
| UEFI serial | UART | Firmware, UniXNU and DarwinBoot |
| Kernel serial | UART selected by `serial=` | XNU console and panic output |
| Diagnostic page | Framebuffer | Live state after the console stops |
| Pulse strip | Framebuffer bottom row | Heartbeat while the diagnostic page owns the panel |
| Panic screen | Framebuffer | Panic text and registers |
| QEMU log | File | UniXNU and loader tests |
| Build reports | JSON | Input hashes and stage results |

## Serial console

Add the arguments to the payload:

```toml
[payload]
kernel_args = ["-v", "serial=3", "debug=0x14e"]
```

The UniXNU boot manager writes to the first `EFI_SERIAL_IO_PROTOCOL` instance. Its lines start with `UNIXNU:`. DarwinBoot lines start with `DARWINBOOT:`.

Capture the port:

```sh
tio -b 115200 -d 8 -p none -s 1 /dev/tty.usbserial-0001 -L out/serial.log
```

Other tools:

```sh
picocom -b 115200 /dev/tty.usbserial-0001
screen -L /dev/tty.usbserial-0001 115200
minicom -D /dev/tty.usbserial-0001 -b 115200
```

The board page records the UART pins and the baud rate. A board with USB device mode can expose a CDC ACM port instead.

Useful early output:

```
UNIXNU: UniXNU 0.1.0 starting as firmware boot option
UNIXNU: config: loaded \EFI\UniXNU\unixnu.toml
UNIXNU: driver ...: started
UNIXNU: menu: shown 2 entries, default 0
DARWINBOOT: loader v2 installed EL1
DARWINBOOT: ARM64 va=... pa=... args=... entry=... owned=...
DARWINBOOT: inputs validated; exiting boot services
```

## On-screen diagnostic page

The diagnostic page is a full-screen text overlay drawn into the XNU framebuffer mapping. Enable it with:

```
boot-progress=1
```

Level 1 arms the monitor. The page freezes when no stage or storage activity appears for 30 seconds, or at the 120 second observation limit, and keeps the screen for a photograph.

```
boot-progress=2
```

Level 2 runs continuously. Deadlines are reported and the OS keeps running.

The page uses 48 rows of 120 columns. On a panel at least 2160 by 1400 the scale is 3.

| Row group | Contents |
| --- | --- |
| Title | Build tag, live or stop state, reason |
| 1 | Time, idle, IRQ count, monitor count, root state, process count, free pages |
| 2 | Storage requests, verified blocks, failures, integrity counters |
| 3 to 30 | Stage history, process states, storage detail, last PC and registers |
| 31 to 47 | Cached storage output, UFS timing, memory, process sampling, UI trace, touch rows |
| 47 | Independent pulse strip |

Label the image so a photograph identifies the build:

```
sheng-build-tag=ks-001
```

The title bar then starts with `[ks-001]`.

When userland takes over the display and stops scanning out, take the panel back:

```
boot-diag-resume=10
```

After 10 seconds without a scanout, the page redraws. A new validated scanout yields the panel again.

The page reports:

| Field | Meaning |
| --- | --- |
| `time` | Seconds since the monitor started |
| `idle` | Seconds since the last stage or I/O progress |
| `IRQ` | Interrupt entries counted by the monitor |
| `monitor` | Monitor thread iterations |
| `lost` | Dropped recorder updates |
| `root` | Owner root acceptance |
| `procs` | Process count |
| `free` | Free 4 KiB pages |
| `requests` | Storage requests |
| `verified4K` | Verified 4 KiB blocks |
| `failures` | Storage failures |
| `integrity` | Storage integrity failures |
| `last PC` | Last interrupt entry PC |
| `TCR`, `TTBR`, `SCTLR` | Translation control and table base registers |

## Pulse strip

The pulse strip is a 32-pixel strip at the bottom of the panel, drawn at 2x scale in green. It runs on a separate high-priority monitor thread at one second intervals.

```
P<turn> I<irq> M<monitor>/<seconds> B<bind>:<result> d<depth> @<base> lock<busy>/<render> PC<pc>
```

| Token | Meaning |
| --- | --- |
| `P` | Pulse turn |
| `I` | Interrupt entries |
| `M` | Monitor count and seconds since it advanced |
| `B` | Framebuffer bind count, result and depth |
| `@` | Framebuffer base |
| `lock` | Recorder and renderer busy flags |
| `PC` | Last interrupt entry PC |

The strip survives while the diagnostic page owns the panel. It closes when the OS takes over the display. `boot-diag-resume` reopens the page and the strip.

## Panic screen

The payload can patch a panic screen into the kernel copy:

```toml
[payload]
panic_screen = true
```

The payload step runs:

```sh
python3 scripts/patch-xnu-entry-probe.py <kernel> --panic-screen --no-reset
```

The main UniXNU repository supplies the entry probe and `xnu-panic-screen.c`. Tree assembly copies them into every device build tree. Panic rendering uses Mu-Silicium’s `Silicon/Silicium/SiliciumPkg/Library/FrameBufferSerialPortLib/Font.h`. Set `uefi` under `[build]` in `unixnu.local.toml`, or run `./unixnu payload --uefi /path/to/Mu-Silicium`. Set `UNIXNU_UEFI` when running the script directly.

The panic screen writes the formatted panic message and registers to the framebuffer and keeps the image visible. `--no-reset` stops the automatic reset, so the screen stays for a photograph.

### Green bar at handoff {#green-bar}

The top green bar is drawn by DarwinBoot's `DarwinEnter` after `ExitBootServices`, before cache maintenance, MMU shutdown, and the branch to XNU. A screen that stays there requires an entry probe or serial log to locate the next stage. The cause is undetermined from the green bar alone.

1. Record the last `DARWINBOOT:` lines, including kernel entry address, video geometry, command line, and CPU state. Confirm the selected kernel and ADT belong to the same device and OS profile.
2. For a kernel supported by `scripts/patch-xnu-entry-probe.py`, set `[payload] panic_screen = true` in the device profile. Rebuild with `./unixnu payload`, then `./unixnu bootimg`, and boot the new image. Check `logs/payload-patch.log` for successful probe installation.
3. Look for the blue and magenta bars below the green band. Blue marks the MMU-off kernel entry; magenta marks the point before enabling the MMU. Check the recorded framebuffer base and stride when probe output is absent.
4. Use `entry_probe_reset_delay = 6` for a timed reset checkpoint after MMU enable. Record the observed bars, reset timing, serial output, and `payload.json` in the device's porting record.

See [applying boot arguments](/xnu/boot-arguments#apply-arguments) when a configuration change is missing from the booted image.

### Color bars

The early boot draws three bands of 1/16 screen height in the frame buffer. In the normal orientation they run from the top:

| Bar | Painted by | Meaning |
| --- | --- | --- |
| Green | DarwinBoot `DarwinEnter` | boot services exited; loader handoff started before the kernel branch |
| Blue | Entry probe stage 1 | the kernel entry code ran with the MMU off |
| Magenta | Entry probe stage 2 | the kernel reached the point just before the MMU is enabled |

The probe places each band below the green one. Stage 3 has no bar: it waits `--reset-delay` seconds after the MMU is on and resets. A reboot after that delay shows the MMU enable completed.

### Entry probe reset

Before the kernel can draw, a reboot is the only signal. `entry_probe_reset_delay` keeps the entry probe's reset: the patched kernel waits that many seconds and resets with PSCI SYSTEM_RESET right after the MMU is on. A reboot after that time shows the CPU got through the MMU enable.

```toml
[payload]
entry_probe_reset_delay = 6
entry_probe_reset_after = "_arm_vm_init"   # optional: reset after this call instead
entry_probe_reset_in = "_arm_init"         # function that makes the call (default)
entry_probe_reset_occurrence = 1           # which call (default 1)
entry_probe_reset_before = false           # reset at the call site, without the call and the delay
```

With `entry_probe_reset_after` the reset moves after that call, so one run answers one question: did the kernel get past it? The keys map to `--reset-delay`, `--reset-after`, `--in`, `--occurrence` and `--reset-before` of the shared `patch-xnu-entry-probe.py`, and they combine with `panic_screen`. Without `entry_probe_reset_delay` the payload keeps `--no-reset`.

The first panic message is also copied to `boot_progress_panic_text`. A panic on a secondary core parks that core; the live banner keeps the text after the screen is repainted.

The device tree panic region is available with:

```
CONFIG_XNU_DT_PANIC_REGION=y
```

The kernel reads `/chosen` `embedded-panic-log-size` and the region `reg` property. The region is validated before it is mapped.

## User fault evidence

The fault probe records EL0 breakpoint and abort state before exception delivery:

| Field | Meaning |
| --- | --- |
| `pid`, `name` | Process |
| `PC`, `LR`, `SP`, `FP` | Registers at the fault |
| `ESR`, `FAR` | Exception syndrome and fault address |
| `slide` | Shared region slide |
| `x0` to `x28` | General registers |
| frames | Up to 12 return addresses |

The capture runs in the trap path without allocation. A matching process exit prints the record with the signal. An uncaught exception reason is searched in the writable malloc regions of the exiting process and printed with the crash row.

## UI stack trace

The UI trace samples the selected processes and prints PC, LR, FP and stack slices:

```
boot-ui-focus=launchd
boot-ui-focus2=SpringBoard
boot-ui-focus3=backboardd
boot-ui-focus4=Setup
boot-ui-chrono=1
```

The address tokens use a radix-64 alphabet to fit in the row width. Feed the transcribed rows to the decoder:

```sh
python3 scripts/decode-boot-ui-trace.py trace.txt
```

The decoder prints one JSON object per thread group with `pc`, `lr`, frames and error codes.

The trace rotates one page every 8 seconds. Take three or four photographs several seconds apart to capture every page.

## Taking photographs

The diagnostic page is built to be photographed. Use this sequence:

1. Set `sheng-build-tag` to a short image label.
2. Enable `boot-progress=1` for a frozen page, or `boot-progress=2` for a live page.
3. Set `boot-diag-resume` when userland blanks the panel.
4. Place the device on a stand. Keep the camera parallel to the panel.
5. Turn off the flash. Light the panel from the side to avoid a reflection.
6. Lock focus and exposure on the title bar.
7. Fill the frame with the panel and include all four corners.
8. Photograph the title bar, then the full page.
9. For UI trace pages, take three or four photos 8 seconds apart.
10. Photograph the bottom pulse strip.
11. Record the boot image SHA-256 and the capture time.

| Check | Why |
| --- | --- |
| Title bar readable | Build tag and state identify the image |
| No glare over text | Rows 3 to 30 carry the stage history |
| All four corners visible | Confirms the full panel and scale |
| Pulse strip visible | Shows the heartbeat at capture time |
| Two or more frames | A changing counter shows a live screen |

A camera photo is evidence of what the panel showed. Keep the original file. Transcribe only the rows you need, and keep the photo with the transcription.

## QEMU capture

```sh
python3 package/Scripts/qemu-run.py out/esp \
  --log out/qemu.log --screenshot out/qemu.png \
  --expect 'UNIXNU: menu: shown'
```

The runner writes the ANSI-stripped log to `out/qemu.clean.log`. `--screenshot` captures the panel when the menu appears. `--keys` sends QEMU key codes after the menu.

The stop helper records registers and memory at a symbol:

```sh
python3 scripts/qemu-entry/gdb-stop.py --help
```

## Debug arguments

| Argument | Use |
| --- | --- |
| `-v` | Verbose kernel output |
| `serial=3` | Serial console |
| `debug=0x14e` | Debug output mask |
| `kextlog=0xfff` | Kext logging |
| `boot-progress=1` | Diagnostic page with a 30 second stall freeze |
| `boot-progress=2` | Diagnostic page with continuous operation |
| `sheng-build-tag=<tag>` | Image label in the title bar |
| `boot-diag-resume=<seconds>` | Take the panel back after the OS stops scanning out |
| `sheng-platform-stage=<n>` | Stop the platform expert at a stage |
| `sheng-touch=<n>` | Touch probe stage |
| `offline-legacy-phase=<n>` | Display probe stage |
| `-no_slto_panic` | Suppress the SLTO panic |
| `cs_debug=<mask>` | Code signing output |

## Evidence bundle

Collect:

| Item | Source |
| --- | --- |
| Serial log | UART capture file |
| Diagnostic photos | Title bar, full page, trace pages, pulse strip |
| Panic photo | Panic screen |
| Boot report | `out/<device>/<os_profile>/<config>/boot/boot.json` |
| Payload report | `out/<device>/<os_profile>/<config>/payload/payload.json` |
| Build logs | `out/<device>/<os_profile>/<config>/logs/` |

Record the boot image hash with every photo:

```sh
shasum -a 256 out/<device>/<os_profile>/<config>/boot/boot.img
jq . out/<device>/<os_profile>/<config>/boot/boot.json
```

## Next steps

- [Boot arguments](/xnu/boot-arguments)
- [Troubleshooting](/reference/troubleshooting)
- [QEMU testing](/reference/qemu)
- [sheng device page](/devices/sheng)
