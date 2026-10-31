# arm64e OS profiles

**Applies to supported devices only.** Use this method only on a device that
meets every [requirement](#requirements) and appears in
[supported devices](#supported-devices). Other devices use the arm64 profile
`ipados-17.7.11-21H461` and the regular [porting steps](/porting/steps).

arm64e needs native PAC hardware: a CPU that implements pointer
authentication and a hypervisor that leaves it usable, as the
[requirements](#requirements) check. A device without it stays on arm64, and
iPadOS 18 is the last version that supports arm64. iPadOS 26 and later are
arm64e only. An arm64e profile builds XNU with pointer authentication (PAC)
and links the original arm64e kexts of the target kernelcache.

For a new port, choose a device whose CPUs have PAC and prefer the iOS or
iPadOS 27 profile. Its drivers, patches and build recipes are the ones under
active maintenance. Every driver and optimization in this repository must work
for 17 and 27, arm64 and arm64e, with the build target as the only difference:
the `--os` parameter of [the packaging script](/porting/packaging). A change that
works for one target only is not merged.

## Requirements {#requirements}

| Requirement | Check |
| --- | --- |
| Every enabled CPU implements FEAT_PAuth with address and generic keys | `ID_AA64ISAR1_EL1` APA or API, and GPA or GPI, are nonzero; or `ID_AA64ISAR2_EL1` APA3 and GPA3 are nonzero |
| XNU runs at EL1 and can write the five key registers | Writing `APIAKey`, `APIBKey`, `APDAKey`, `APDBKey` and `APGAKey` at EL1 does not trap |
| PAC instructions do not trap at EL1 and EL0 | `PACIA` changes a pointer and `AUTIA` restores it on every core |
| SoC support exists | The SoC repository is listed in [SoC support](/porting/soc-support) |
| Native 4 KiB stage 1 translation | Same as the arm64 profile, see [four-kilobyte pages](/xnu/four-k-page-tables) |

A hypervisor that clears `HCR_EL2.APK` or `HCR_EL2.API` traps these accesses.
Record the result of each check in the device `porting.toml`.

## Supported devices {#supported-devices}

| Device | SoC | OS profile | State |
| --- | --- | --- | --- |
| sheng | SM8550 | `ipados-27.0.1-24A446` | In development |
| sheng | SM8550 | `ipados-26.5.2-23F84` | Kept as the earlier arm64e profile |

## Profile layout

| Location | Contents |
| --- | --- |
| `profiles/arch/arm64e` | arm64e build configuration, PAC key management and XNU patch series |
| `profiles/os/ipados-27.0.1-24A446` | XNU `12377.121.6` with the Darwin 26 calls, iPadOS 27.0.1 IPSW pins, prelink roots and OS patches |
| `profiles/os/ipados-26.5.2-23F84` | The earlier arm64e profile, same XNU revision and its own IPSW pins |

The OS profile selects its architecture with `[os] arch = "arm64e"`. Profiles
without the key use `profiles/arch/arm64`. Both architectures use the same
components; the arm64e build compiles them for arm64e.

## Pointer authentication

An arm64e image stores authenticated pointers as chained fixups that name a
key and a diversifier. dyld signs user pointers when it loads an image, and
XNU signs kernel collection pointers during early boot. No signature is
computed off the device, so the CPU's PAC algorithm does not need to match
Apple's.

Public XNU source programs keys only for the paravirtualized `VMAPPLE`
platform, in `osfmk/arm64/pac_asm.h`. The arm64e profile supplies native key
programming for ARMv8.3 key registers.

On ARMv8.3, EL0 and EL1 use the same key registers. The current profile loads
one random key set per boot on every CPU and enables `SCTLR_EL1` EnIA, EnIB,
EnDA and EnDB. The kernel and all processes share this key set, so PAC does not
isolate processes from each other.

## CPU features

XNU publishes only the features the CPU implements, through `hw.optional`
sysctls and the commpage capability words. SM8550 has no SME. The iPadOS
26.5.2 dyld cache contains SME code in functions with SME-specific names.

## Procedure

1. Run the [requirement](#requirements) checks on every enabled CPU and record them.
2. Set `board.os_profile = "ipados-27.0.1-24A446"` in the device configuration, or pass
   `--os 27` to `./unixnu` for one run.
3. Run `./unixnu fetch` and `./unixnu status --json`. Confirm the arm64e profile, XNU revision and patch order.
4. Build with [Building](/building): kernel, package, firmware, payload, userdata, boot image.
5. Follow the [bring-up order](/porting/bring-up) and record each checkpoint.

## Facts and open questions

Facts:

- The iPadOS 26.5.2 kernelcache for iPad17,1 to iPad17,4 reports `xnu-12377.122.8`. The closest public source is `xnu-12377.121.6`.
- The public `xnu-12377.121.6` tree keeps the non-SPTM pmap in `osfmk/arm/pmap`.
- The arm64e kernel builds with the `BCM2837` machine config, the non-SPTM pmap and Apple CPU counters disabled.
- The iPadOS 26.5.2 kernelcache is an `MH_FILESET` with stripped symbol tables. Its kext code branches directly into the kernel, so the iPadOS 17 prelink step does not apply.

Open questions:

- The SME functions in the dyld cache are probably selected at run time from the published CPU features. This is not yet confirmed.
