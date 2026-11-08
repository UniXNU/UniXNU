# Boot arguments

## Apply boot arguments {#apply-arguments}

The effective command line combines `[payload] kernel_args` in the board profile, `[build] kernel_args` in `unixnu.local.toml`, and `--kernel-arg` overrides. Later sources replace arguments with the same name. The payload builder writes it to `EFI/UniXNU/unixnu.toml` as the XNU entry's `args`. UniXNU passes the selected entry to DarwinBoot, which copies the line into XNU's `boot_args.CommandLine` at boot. Kernel configuration switches are compiled by `./unixnu kernel`.

With [local build inputs](/reference/configuration#local-build-inputs) saved:

```sh
./unixnu payload --kernel-arg serial=3 --kernel-arg debug=0x14e
./unixnu bootimg
jq -r .kernel_args out/<device>/<os_profile>/<config>/payload/payload.json
mtype -i out/<device>/<os_profile>/<config>/payload/payload.img ::/EFI/UniXNU/unixnu.toml
```

Boot the newly generated `boot/boot.img`. `bootimg` copies the current payload into that file. Editing a payload after packaging requires running `bootimg` again. A custom `--ramdisk FILE` selects that file's configuration. Check the XNU entry you select and any appended `confirm_args`. When several volumes contain `unixnu.toml`, check the configuration on the boot manager's own volume first.

The payload command prints `kernel args:` and DarwinBoot prints `DARWINBOOT: command line:` before handoff. If they differ, inspect the selected volume and entry. If they match and behavior is unchanged, check that the kernel or selected driver implements the argument. A green handoff bar is covered in [early boot diagnosis](/guide/debugging#green-bar).

## Format

An argument matches:

```
[A-Za-z0-9_.-]+(=[A-Za-z0-9_.,-]+)?
```

The joined line is at most 1000 bytes. DarwinBoot copies it into a 1024-byte buffer.

```sh
./unixnu build payload --kernel-arg serial=3 --kernel-arg debug=0x14e
```

## Common arguments

| Argument | Purpose |
| --- | --- |
| `-v` | Verbose kernel output |
| `serial=3` | Selects the serial console |
| `debug=0x14e` | Enables the debug output mask |
| `kextlog=0xfff` | Verbose kext logging |
| `-apfs_shared_datavolume` | Uses the shared APFS data volume |
| `-no_slto_panic` | Suppresses the SLTO panic |
| `kt_fixed_zones=<n>` | Fixes the kernel trace zone count |
| `boot-progress=<n>` | Selects the boot progress display level |
| `cs_debug=<mask>` | Code signing debug output |
| `amfi_get_out_of_my_way=1` | Runs without AMFI enforcement |
| `pmap_debug=<mask>` | Pmap debug output |
| `zlog=<name>` | Selects the zone log |

Use `amfi_get_out_of_my_way=1` only in a diagnostic boot. It changes the security policy.

## Platform arguments

| Argument | Purpose |
| --- | --- |
| `sheng-platform-stage=<n>` | Stops the platform expert at a fixed stage |
| `sheng-pmgr=<n>` | Selects the board PMGR integration |
| `native-ufs-root=1` | Uses the native UFS root path |
| `native-ufs-stats-delay=<n>` | Delays the UFS statistics read |
| `armcpu-diagnostics=1` | Prints the CPU and interrupt state |
| `armcpu-spi-ipi=1` | Uses the SPI path for inter-processor interrupts |
| `sheng-smp=1` | Starts the secondary CPUs |
| `sheng-cpufreq=<n>` | Selects the CPU frequency path |
| `sheng-touch=<n>` | Runs the touch probe stage |
| `sheng-touch-hz=<n>` | Selects the touch SPI clock |
| `sheng-touch-mode=<n>` | Forces the touch SPI mode |
| `sheng-touch-hid=1` | Publishes touch contacts to HID |
| `sheng-aks=1` | Enables the AKS path |
| `sheng-aks-sls=<n>` | Selects the reported lock state; 3 means no passcode |
| `sheng-usb=<n>` | Runs QcomDwc3; 2 adds register sampling, 3 also cycles the bus once |
| `sheng-usb-host=<s>` | Forces USB host mode after a delay |
| `sheng-usb-back=<s>` | Returns to the cable's role after this time in forced host mode |
| `sheng-gpu-power=<n>` | Selects the GPU power sequence |
| `sheng-gpu-metal=1` | Enables the Metal path |
| `sheng-gpu-addon=1` | Mounts the GPU addon content |
| `sheng-data-persist=<n>` | 1 proves the Data store window read-only, 2 opens it for writes |
| `sheng-data-reset=<n>` | 1 discards the Data overlay, 2 also asks for Setup |
| `sheng-log-reserve=<mib>` | End-of-userdata reserve for the diagnostic log and export region, default 1024 |
| `sheng-data-fua=1` | Runs the Data store write through (every write with FUA) instead of write back |
| `sheng-ufs-bench=1` | Runs the UFS read benchmark before the boot goes on, logs it and restarts into fastboot |
| `sheng-disable-watchdogd=1` | Stops the watchdog daemon |
| `sheng-disable-jobs=<list>` | Skips the named launch jobs |
| `offline-legacy-*=1` | Enables the legacy display and input probes |
| `offline-owner-root-check=1` | Starts the verified root check |
| `offline-owner-root-audit=1` | Enables the root binding audit |
| `offline-apfs-load=1` | Loads APFS at the offline checkpoint |
| `offline-mobile-graphics-*=1` | Enables the mobile graphics probes |
| `boot-ui-focus=<name>` | Selects the process for the boot UI trace |

The list above includes board specific arguments. Check the device page and the board file for the set a device uses.

## Adding an argument

1. Add the default to `[payload] kernel_args`.
2. Add a one-off value with `--kernel-arg`.
3. Read the value in the kernel with `PE_parse_boot_argn`:

```c
unsigned stage = 0;
if (PE_parse_boot_argn("my-driver-stage", &stage, sizeof(stage))) {
  ...
}
```

4. Document the argument in the device page.

## Debugging

| Need | Arguments |
| --- | --- |
| Early kernel output | `-v serial=3 debug=0x14e` |
| Kext load detail | `kextlog=0xfff` |
| Boot progress | `boot-progress=2` |
| Platform stop | `sheng-platform-stage=<n>` |
| Storage detail | `native-ufs-root=1 native-ufs-stats-delay=30` |
| Display detail | `offline-legacy-gop=1 offline-legacy-phase=<n>` |
| Code signing detail | `cs_debug=<mask>` |

A panic log records the last kernel output. The embedded panic region is read from the device tree when `XNU_DT_PANIC_REGION` is set.

## Next steps

- [Troubleshooting](/reference/troubleshooting)
- [Boot the image](/guide/boot)
- [Devices](/devices/)
