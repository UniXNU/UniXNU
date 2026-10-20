# Boot arguments

The kernel command line comes from `[payload] kernel_args` in the board file. An extra `--kernel-arg NAME=VALUE` replaces the board argument with the same name. The payload step writes the joined line into `unixnu.toml`, and DarwinBoot copies it into `boot_args`.

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
| `sheng-gpu-power=<n>` | Selects the GPU power sequence |
| `sheng-gpu-metal=1` | Enables the Metal path |
| `sheng-gpu-addon=1` | Mounts the GPU addon content |
| `sheng-data-persist=<n>` | 1 proves the Data store window read-only, 2 opens it for writes |
| `sheng-data-reset=<n>` | 1 discards the Data overlay, 2 also asks for Setup |
| `sheng-log-reserve=<mib>` | End-of-userdata reserve for the diagnostic log and export region, default 1024 |
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
