# Capture logs and automate boot tests

Set up log capture as you bring up the board. Start with firmware logs, collect
kernel evidence at handoff, then add persistent logs and automated reboot cycles.
Use the [bring-up checkpoints](/porting/bring-up) to identify the stage being tested.

| Stage | Required support | Saved result |
| --- | --- | --- |
| UEFI menu | GOP display, menu input, Advanced Logger and QR plugin | Firmware `.log` file scanned from the screen |
| XNU entry | UART or framebuffer diagnostics | Serial log or photograph of the last checkpoint/panic |
| Storage | Reserved log region, kernel writer and a Linux or recovery reader | Kernel message buffer and diagnostic snapshots |
| Repeated tests | Working log retrieval and return to bootloader | One evidence directory per boot |

## 1. Include the firmware log exporter {#firmware-setup}

Prepare the firmware checkout using [UEFI integration](/porting/uefi-firmware).
The shared exporter is
`package/UniXNUPkg/Driver/AdvancedLogDxe/AdvancedLogDxe.inf` in UniXNU.
It reads the Advanced Logger memory buffer while UEFI boot services are active.

1. In the firmware DSC `[Components]`, add:

   ```ini
   UniXNUPkg/Driver/AdvancedLogDxe/AdvancedLogDxe.inf
   ```

   In the FDF's DXE firmware volume, add:

   ```ini
   INF UniXNUPkg/Driver/AdvancedLogDxe/AdvancedLogDxe.inf
   ```

2. Enable the platform's Advanced Logger producer and route the desired firmware
   debug output into it. The exporter dispatches after `gAdvancedLoggerProtocolGuid`
   is installed. Its INF also requires `AdvLoggerPkg`, `MsGraphicsPkg`,
   `AdvancedLoggerAccessLib` and `QrEncoderLib`.
   From the firmware checkout, find the library instances supplied by its Mu revision:

   ```sh
   find . -name '*AdvancedLogger*.inf' -o -name '*QrEncoder*.inf'
   ```

   Map the access and QR libraries in the DSC `[LibraryClasses]` and include their
   package roots in `board.toml` `[firmware] packages`. Initialize the submodules
   containing those packages if the search returns no files. Use the platform's
   Advanced Logger configuration for its buffer and debug-library mappings.

3. Set `gUniXNUPkgTokenSpaceGuid.PcdUniXNUDeviceModel` in the DSC `[PcdsFixedAtBuild]`
   to the board's ASCII name. The export filename uses this value.
4. In the device's `board.toml`, add `tools = true` to its existing `[payload]`
   table. This adds **Tools** to the generated boot menu. A hand-authored
   `unixnu.toml` uses an [entry with `action = "tools"`](/reference/boot-configuration).
5. From the main UniXNU checkout, with the device selected and
   [local inputs configured](/reference/configuration#local-build-inputs), run:

   ```sh
   ./unixnu firmware
   ./unixnu payload
   ./unixnu bootimg
   ```

**Result:** the rebuilt image contains the exporter, and **Tools → Advanced Logger**
appears when the platform's logging protocol is available.

## 2. Scan the firmware log before kernel handoff {#qr-logs}

Prepare a second phone or camera device with [OneSend (扫传)](https://onesend.01mvp.com).
The exporter sends a sequence of OneSend QR frames.

1. Boot the image from the main checkout:

   ```sh
   fastboot devices
   fastboot -s <serial> boot out/<device>/<os_profile>/<config>/boot/boot.img
   ```

2. Stay in the UniXNU menu. Select **Tools**, then **Advanced Logger**.
   The plugin takes a snapshot of the current firmware log when opened.
   If a loader error returns you to the menu, open the plugin then to capture it
   before resetting the device.
3. Open OneSend's receiving scanner, allow camera access and keep the complete QR
   square in view. Keep scanning as frames cycle until the receiver finishes.
4. Use **Down / j** to slow rotation and **Up / k** to speed it up. The initial
   interval is one second; five speeds range from 5 seconds to 250 milliseconds.
   Boards that map volume buttons to Up/Down use those buttons. **Enter** or
   **Escape** returns to the menu; a board's power button works when mapped to Enter.
5. Save the received `<model>-<date>-<time>.log` with the image revision and last
   completed checkpoint. The filename uses the firmware clock. Check the text for
   the failing operation before rebuilding.

**Result:** a readable firmware log captured while the menu remains accessible.
XNU execution after `ExitBootServices` uses the capture methods in step 3.

| Symptom | Action |
| --- | --- |
| Tools is missing | Check `[payload] tools`, rebuild the payload and repack the boot image |
| Advanced Logger is missing | Check the INF in DSC/FDF, its dependencies and the platform's logger protocol |
| `Advanced Logger: no log` | Check the Advanced Logger producer, debug routing and buffer configuration |
| Scanner progress stops | Reduce rotation speed and keep scanning the repeating sequence |
| Firmware stops before the menu | Capture the platform UART or photograph its last visible output |

## 3. Capture the kernel handoff {#kernel-logs}

1. Save the firmware log from step 2, then start the kernel entry.
2. Follow [debugging](/guide/debugging#procedure) to capture the board's UART or
   framebuffer output. For a green handoff bar, use the
   [entry-probe procedure](/guide/debugging#green-bar).
3. Photograph the complete panic screen or checkpoint, including registers and
   the last text lines. Record the kernel arguments from the built payload.
4. After changing arguments, run `./unixnu payload` and `./unixnu bootimg` again.
   Repeat the same boot and compare the last confirmed checkpoint.

**Result:** evidence for the kernel stage even while storage is being adapted.
Continue with persistent capture after [storage verification](/porting/ufs).

## 4. Select a persistent log reader {#persistent-logs}

A persistent reader consumes the reserved log region after the test kernel
returns control. Define the region, file header, boot ID, completion marker and
snapshot layout before implementing the reader. The writer, reader and decoder
must use the same block units and byte ranges.

1. Reserve a log region in the target storage layout. Record its partition,
   offset, size and block units beside the root and Data regions. Check that the
   image builder, partition provider, writer and reader use the same bounds.
2. Connect the kernel writer to the storage driver's bounded read, write and
   sync operations. Store the kernel message buffer, diagnostic snapshots, boot
   ID and write status. Start the writer after the region opens.
3. Choose a reader environment that the device can boot:

   **Linux reader.** Build a small Linux image with the target kernel, DTB,
   storage driver, USB device controller and CDC ACM support. Copy the region
   into RAM, expose a serial shell and keep source partitions read-only.

   **Recovery reader.** Boot a compatible rooted recovery image with block
   access and ADB, then read the region from recovery. A TWRP-like recovery
   provides the reader runtime; the host only transfers the result.

   ```sh
   adb reboot recovery
   adb wait-for-device
   adb shell id
   adb shell ls -l /dev/block/by-name
   adb shell mkdir -p /tmp/unixnu-log
   adb shell dd if=/dev/block/by-name/<log-partition> \\
     of=/tmp/unixnu-log/log.bin bs=4M
   adb pull /tmp/unixnu-log/log.bin out/logs/log.bin
   ```

   For a region inside `userdata`, use the offset and length from the device
   record with `dd skip=<block-offset> count=<block-count>`. Keep the recovery
   mount read-only. Record the recovery build, block path and command.
4. Adapt the host decoder to the writer header and snapshot format. Select the
   serial device or ADB target explicitly when automatic discovery does not
   identify one device.
5. Implement the return path for the selected reader. Use the board's reboot
   reason and reset interface. Record the bootloader and recovery commands used
   by the manual cycle.

The [sheng implementation](https://github.com/UniXNU/UniXNU-sheng) supplies a
Linux reader, a reserved `userdata` region and a fastboot return path. Its source
layout is a reference for `package/BootLog.c`, `BootReset.c`,
`BootResetCore.h`, `package/linux-log/` and `scripts/read-sheng-log.py`. Its PMIC
addresses, watchdog calls, storage reservation and Linux image inputs belong to
that board record.

**Result:** one reader environment, one matching decoder, an identified storage
range and a tested route back to bootloader or recovery.

For the sheng iPadOS 27 native source path, enable sheng-log=1 boot-ui-trace=1
when diagnosing a user-space stall. The source storage archive includes
BootProcessWorker.c, which captures process stacks separately from the log
writer so a user-page fault cannot stop log persistence. Add
boot-ui-focus3=chronod to retain its stacks alongside backboardd and SpringBoard.
The arm64e sampler strips return-address PAC before validating and encoding
frames. An empty stack section alone is not evidence that the processes stopped.

## 5. Complete one manual capture cycle {#manual-cycle}

1. Build a test payload with logging enabled and rebuild the boot image.
2. Boot the test image and wait for the checkpoint under test.
3. Return to the selected reader environment:

   ```sh
   fastboot -s <serial> boot <reader.img>
   ```

   Or boot the recovery image:

   ```sh
   adb reboot recovery
   adb wait-for-device
   ```
4. Run the reader, save the raw region and decoded text under a directory named
   with the boot ID, and confirm the header, snapshots and write status.
5. Return to the board's bootloader and confirm its identity before the next run.

The selected device repository supplies the Linux reader commands. The recovery
commands above apply to any board with a compatible recovery image.

**Result:** one complete test, an identifiable evidence directory and a verified
reader return path. A missing or stale header points to writer startup, region
geometry or the selected reader command.

## 6. Automate the verified cycle {#automated-cycle}

1. Enable the board's timed return to bootloader or recovery. Set the timeout
   after the measured checkpoint and log synchronization time.
2. Configure a host runner with the exact device identity, test image, reader
   image or recovery image, output directory and timeout.
3. Have it boot the test image, observe the return, start the selected reader,
   retrieve and decode the log, and confirm the final bootloader state.
   A recovery reader uses `adb reboot recovery`, `adb wait-for-device` and
   `adb pull` in the same sequence as the manual cycle.
4. On timeout, record the failed stage and use the board's documented bootloader
   or recovery entry procedure. Keep the images and partial evidence.
5. Repeat after one change. Record revisions, arguments, checkpoint, reset
   result, reader environment, output directory and unresolved errors in the
   [porting record](/porting/records).

The runner follows the same sequence as the manual cycle. A board with recovery
access can use the same runner structure with ADB commands.

**Result:** each test produces an identifiable evidence directory and a recorded
return path. Continue the remaining [bring-up stages](/porting/bring-up).
