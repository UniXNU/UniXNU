# UniXNU partition (experimental)

`scripts/dual_sys/partition.py` detects the device and partition layout through ADB, shrinks F2FS, then creates `unixnu` from the end of `userdata`. Specify the new partition size in GiB.

It preserves userdata's start, type, GUID and attributes. The new block device is `/dev/block/by-name/unixnu`; formatting, OS installation and boot configuration are separate steps.

## Supported layout

| Requirement | Accepted state |
| --- | --- |
| Host | Python 3.10 or newer, Android platform-tools; no Python packages required |
| Recovery | Compatible TWRP with root ADB and working `/data` decryption |
| Kernel | Implements `F2FS_IOC_RESIZE_FS` for online shrinking; validate the recovery kernel for the device |
| Filesystem | F2FS, 4096-byte blocks, 512 blocks per segment, one segment per section, checkpoints enabled |
| Encryption | Direct userdata, or one full-length device-mapper mapping backed only by userdata |
| Partition table | Matching primary and backup GPT, 512- or 4096-byte logical sectors, conventional 128-byte entries |
| Partition placement | `userdata` is the last occupied partition; an unused GPT entry exists; `unixnu` does not exist |
| Recovery commands | `sh`, `dd`, `blockdev`, `sha256sum`, `cmp`, `readlink`, `sync`, `umount` |

Unsupported layouts stop the script: Ext4, multi-device or zoned F2FS, multiple segments per section, encryption footers, stacked mappings and intervening partitions.

## Prepare recovery (optional partition backup)

1. Enter compatible TWRP. If already installed:

   ```sh
   adb reboot recovery
   adb devices -l
   ```

2. Inspect the device and GPT. With multiple devices, add `--serial SERIAL` to each host-script command.

   ```sh
   python3 scripts/dual_sys/partition.py inspect
   ```

3. Optional: save the original boot/recovery images and back up offline `userdata` and `metadata` together to another physical disk. TWRP file backups may omit encryption metadata. To skip partition backups, continue to step 4.

   Disable MTP; unmount Data, its bind mounts and Metadata. Confirm that neither partition nor its decrypted view remains mounted:

   ```sh
   adb -s SERIAL shell cat /proc/mounts
   adb -s SERIAL shell readlink -f /dev/block/by-name/userdata
   adb -s SERIAL shell readlink -f /dev/block/by-name/metadata
   ```

   Once offline, copy both partitions in a POSIX host shell. Replace the backup path and `SERIAL`:

   ```sh
   mkdir -p /external-disk/phone-backup
   adb -s SERIAL exec-out 'dd if=/dev/block/by-name/metadata bs=1048576 2>/dev/null' \
     > /external-disk/phone-backup/metadata.img
   adb -s SERIAL exec-out 'dd if=/dev/block/by-name/userdata bs=1048576 2>/dev/null' \
     > /external-disk/phone-backup/userdata.img
   adb -s SERIAL shell blockdev --getsize64 /dev/block/by-name/metadata
   adb -s SERIAL shell blockdev --getsize64 /dev/block/by-name/userdata
   wc -c /external-disk/phone-backup/metadata.img /external-disk/phone-backup/userdata.img
   shasum -a 256 /external-disk/phone-backup/metadata.img /external-disk/phone-backup/userdata.img
   ```

   Require successful copies and matching file/device sizes. On Windows, use a binary-safe backup tool, not a PowerShell text pipeline. Retain these backups.

4. Restart TWRP, decrypt Data and mount `/data` read-write. Keep MTP off and close programs using `/data`:

   ```sh
   adb -s SERIAL reboot recovery
   adb -s SERIAL wait-for-device
   # Decrypt and mount Data in TWRP, then inspect it.
   adb -s SERIAL shell cat /proc/mounts
   ```

5. Partition backups are optional. Consider saving important data before shrinking.

## Build the recovery helper

Match the architecture shown by `inspect`. For AArch64, build a static helper with a Linux cross compiler:

```sh
mkdir -p out/dual_sys
aarch64-linux-gnu-gcc -static -O2 -Wall -Wextra -Werror \
  scripts/dual_sys/f2fs-shrink.c -o out/dual_sys/f2fs-shrink
file out/dual_sys/f2fs-shrink
```

Verify that the output is a static AArch64 ELF. Static musl builds also work. The host script checks its architecture and uploads it to recovery `/tmp`.

## Preview the split

Example: reserve 32 GiB for UniXNU.

```sh
python3 scripts/dual_sys/partition.py plan \
  --size-gib 32 --helper out/dual_sys/f2fs-shrink \
  --output out/dual_sys/preview
```

`--size-gib`: positive GiB value in whole MiB increments, such as `32` or `32.5`. Capacity equals the request; boundaries align to 1 MiB, leaving any smaller trailing fragment unallocated. Review the printed layout. Use a new output directory.

`plan` checks GPT, F2FS, free space and device mappings. It writes only host files and recovery `/tmp`.

| Bundle file | Purpose |
| --- | --- |
| `plan.json` | Device identity, original filesystem state and calculated partition ranges |
| `gpt-primary.before`, `gpt-backup.before` | Original GPT regions, including the protective MBR in the primary region |
| `gpt-primary.after`, `gpt-backup.after` | Proposed GPT regions |
| `plan.env` | Device paths, sizes and expected results for the recovery script |
| `twrp.sh`, `f2fs-shrink` | Recovery execution script and compiled helper |
| `SHA256SUMS` | Detects incomplete transfer or changes to the generated bundle |

Keep this bundle; if you made userdata/metadata backups, store them alongside it. GPT backups cannot restore lost file contents.

## Apply the split

`apply` generates a fresh plan. Use the same size and a new output directory.

```sh
python3 scripts/dual_sys/partition.py apply \
  --size-gib 32 --helper out/dual_sys/f2fs-shrink \
  --output out/dual_sys/applied
```

Check the device and layout, then enter the displayed confirmation phrase exactly. Keep power connected and leave TWRP idle.

Execution order:

1. Recheck the bundle, device, kernel and GPT.
2. Shrink F2FS through the kernel.
3. Verify both superblocks fit the new userdata range.
4. Unmount `/data`; reject remaining mounts.
5. Write and read back backup GPT, then primary GPT; recheck both from the host.

`metadata` remains unchanged. `/data` stays unmounted until a manual recovery restart refreshes the partition table. GPT writes follow the [UEFI backup-first order](https://uefi.org/specs/UEFI/2.9_A/05_GUID_Partition_Table_Format.html).

The host invokes `twrp.sh` with the generated `plan.env`. For a manual check, substitute the printed recovery directory:

```sh
adb -s SERIAL shell 'sh /tmp/unixnu-dual-REPLACE_WITH_PRINTED_ID/twrp.sh check'
```

Bundles are device- and session-specific. Use host `apply` to generate a fresh execution plan.

## Verify after restarting recovery

After successful GPT readback, restart recovery to refresh partition sizes and encryption mappings. Decrypt and mount Data, then verify:

```sh
adb -s SERIAL reboot recovery
adb -s SERIAL wait-for-device
# Decrypt and mount Data in TWRP.
python3 scripts/dual_sys/partition.py verify --plan out/dual_sys/applied/plan.json
```

`verify` checks GPT, kernel partition ranges and F2FS size. Confirm files are readable, then test Android boot:

```sh
adb -s SERIAL reboot system
```

`unixnu` remains unformatted and may contain old userdata bytes. Before writing an image, check that the device port and flash command target `unixnu`: the default build command may still target Android's `userdata`. Image-builder and UFS-driver configuration remain separate tasks.

## F2FS size calculation

For original block count `B`, partition limit `L` in 4096-byte blocks and section size `S = 512`, the request is `floor((L - B % S) / S) * S`. The [kernel](https://github.com/torvalds/linux/blob/v6.6/fs/f2fs/gc.c) removes whole sections and retains the original remainder; rounding `L` alone can exceed the new partition. The helper checks the final size.

## Interrupted operations

No automatic retry or rollback is provided. Do not delete the recovery-session lock to rerun `apply`. Before restarting recovery, save the stage and kernel log:

```sh
adb -s SERIAL pull /tmp/unixnu-dual-REPLACE_WITH_PRINTED_ID/stage ./recovery-stage.txt
adb -s SERIAL shell dmesg > recovery-dmesg.txt
```

| Last completed operation | Next action |
| --- | --- |
| Planning or prechecks | Storage is unchanged; resolve the reported condition and make a fresh plan |
| F2FS resize failed | Keep the original GPT; inspect filesystem/kernel errors before another attempt |
| F2FS verified, unmount failed | GPT remains original; inspect open files and bind mounts; never force or lazily unmount |
| Backup GPT write started | Copies can disagree; keep recovery running and inspect both raw copies before rebooting |
| Both GPT copies read back successfully | Restart recovery and run `verify` |

Do not format unreadable Data. Restoring GPT does not undo F2FS relocation. A full userdata restore requires the original partition capacity and matching metadata backup. Have the device maintainer assess the captured state first.

## Offline tests

Linux, WSL and macOS; a C compiler is required. No phone required:

```sh
python3 scripts/dual_sys/test_dual_sys.py
cc -O2 -Wall -Wextra -Werror scripts/dual_sys/f2fs-shrink.c -o /tmp/f2fs-shrink-test
/tmp/f2fs-shrink-test self-test
sh -n scripts/dual_sys/twrp.sh
```

On macOS, `cc` builds only the shared rounding self-test, without Linux headers or device operations. Use the Linux/Android ELF build above for recovery.

Coverage: GPT, F2FS rounding, ADB selection and simulated failure ordering. Recovery-kernel behavior, data integrity and Android boot still require hardware tests.
