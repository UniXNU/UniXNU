# QEMU testing

QEMU tests UniXNU, the injection paths, DarwinBoot and the kernel entry without a device.

## Requirements

| Tool | Purpose |
| --- | --- |
| `qemu-system-aarch64` | AArch64 virtual machine |
| AAVMF or EDK2 AArch64 firmware | UEFI environment |
| `dtc` | Device tree compilation |
| `mtools` or `pyfatfs` | FAT image for the block slice test |

The QEMU runner looks for the firmware in the common Homebrew and distribution paths, or takes `--firmware`.

## Stage an ESP

```sh
python3 package/Scripts/stage-esp.py -o out/esp \
  package/UniXNUPkg/Test/Qemu/esp \
  --put out/<board>/package/Build/Out/UniXNU.efi=EFI/BOOT/BOOTAA64.EFI \
  --put out/<board>/package/Build/Out/HelloPayload.efi=EFI/UniXNU/Payloads/HelloPayload.efi \
  --put out/<board>/package/Build/Out/SampleDriver.efi=EFI/UniXNU/Kits/SampleDriver.kit/SampleDriver.efi
```

`stage-esp.py` copies the tree, compiles `.dts` to `.dtb` and `.dtso` to `.dtbo`, and places each `--put` file at its destination.

## Run

```sh
python3 package/Scripts/qemu-run.py out/esp \
  --log out/qemu.log --screenshot out/menu.png \
  --expect 'UNIXNU: menu: shown' \
  --expect 'UNIXNU-HELLO: RESULT PASS'
```

| Option | Meaning |
| --- | --- |
| `--firmware FILE` | AAVMF code image |
| `--log FILE` | Serial log |
| `--screenshot FILE` | PNG captured when the menu appears |
| `--keys LIST` | QEMU key codes sent after the menu |
| `--expect REGEX` | Pattern that must match the serial log |
| `--reject REGEX` | Pattern that must not match |
| `--no-gop` | No display device, text console only |
| `--display-size WxH` | Virtio GPU display of this size instead of ramfb, for example `1080x2400` for a portrait panel. The firmware needs at least 640 pixels of width |
| `--disk FILE` | Extra read-only raw disk |
| `--timeout SECONDS` | Run timeout |
| `--cpus N` | Virtual CPU count |
| `--finish-on-expect` | Stop two seconds after all expectations match |
| `--menu-marker TEXT` | Log marker that triggers the screenshot and keys |

The runner exposes the ESP read-only through QEMU `vvfat`, captures the serial log, and talks to QEMU over QMP for screenshots and keys.

## Smoke test

```sh
JOBS=8 bash package/Scripts/smoke.sh
```

The script builds the package and runs six scenarios:

| Scenario | Checks |
| --- | --- |
| Default entry | Device tree patches, overlay, kit driver, initrd media, entry variable |
| Keyboard | Down and Enter select the second entry |
| Degraded | No GOP and no configuration, built-in entries, text console |
| Block slice | Configuration on a FAT partition head, tail published as a block device |
| Kext staging | Revision 2 handoff, revision 1 refusal, invalid bundles, duplicates |
| Layout | A 1080x2400 display uses portrait, an 800x1000 display stays landscape |

Logs and screenshots go to `package/Build/Smoke/`.

## XNU entry fixture

The QEMU entry generator builds an Apple-format device tree for the kernel:

```sh
python3 scripts/qemu-entry/make-dt.py \
  --armvirt --armcpu --smp 2 \
  --owned-memory-size 0x20000000 \
  --output build/qemu-test.adt
```

| Option | Meaning |
| --- | --- |
| `--armvirt` | Describe QEMU virt devices |
| `--armcpu` | Add the GICv3 distributor and redistributor |
| `--smp N` | CPU count and PSCI |
| `--owned-memory-size` | Contiguous DarwinBoot window |
| `--data-ramdisk` | Scratch Data placeholder |
| `--trust-cache` | Trust cache placeholder |
| `--nvram-proxy` | Volatile CHRP NVRAM proxy |
| `--root-match-volume-uuid` | Root volume match |
| `--osenvironment` | `main`, `recoveryos` or `ramdisk` |
| `--qemu-vmm-present` | Report the VMM in `/defaults` |
| `--crypto-hash-method` | Image4 hash method |

The generator describes QEMU and uses QEMU values only.

## HVF

On Apple Silicon macOS, QEMU can use HVF:

```sh
python3 scripts/qemu-entry/make-dt.py --armvirt --armcpu --qemu-vmm-present \
  --qemu-accel hvf --output build/qemu-hvf.adt
```

The generator reads the host counter frequency for the CPU timebase. The bound fixture is used to observe the actual `TCR_EL1`, `SCTLR_EL1` and `TTBR` registers at the kernel stop point.

## Stop point

```sh
python3 scripts/qemu-entry/gdb-stop.py --help
```

The helper stops QEMU at a symbol and records registers, memory and the last checkpoint. The output is a JSON report.

## Next steps

- [Bring-up order](/porting/bring-up)
- [Four-kilobyte pages](/xnu/four-k-page-tables)
- [Troubleshooting](/reference/troubleshooting)
