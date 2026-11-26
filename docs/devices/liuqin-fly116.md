# Xiaomi Pad 6 Pro \(liuqin\): storage chain up, root mount not reached \(Fly116\)

[Fly116/UniXNU-liuqin](https://github.com/Fly116/UniXNU-liuqin)

UniXNU port record for the Xiaomi Pad 6 Pro \(liuqin / SM8475\). The UFS storage chain, the iOS root image and block-device publication are working on hardware; the root volume is **not** mounted yet, and this tree **cannot boot an iOS user interface**.

Target components: iPad7,1 iPadOS 17.7.11 \(21H461\).

| Part | Status |
| --- | --- |
| Configuration | `implemented` \(board.toml + liuqinPkg\) |
| Firmware and boot | `implemented` \(Mu-Silicium UEFI + BootShim, built entirely on Linux\) |
| Memory and DMA | `implemented` \(private contiguous allocation + `kmem_alloc_contig`\) |
| Display | `implemented` \(framebuffer text console only\) |
| Storage and root volume | `partial`: UFS link, GPT/SHNGROOT parsing and block publication work; no `IOMedia`, root not mounted |
| Packaging | `implemented` \(userdata 94 GiB + `unixnu` 11.79 GiB, image 9,382,658,048 B\) |
| Userland | `planned` |
| GPU / user interface | `planned`; no Metal driver on Adreno, a real SpringBoard is unlikely on this route |
| Network, audio, power | `planned` |

## Verified findings

- No driver initialises `IOMapper` off-Apple hardware, and a wired descriptor\'s `prepare()` never returns; a private DMA buffer replaces it.
- Early `kmem_alloc_contig` is unreliable and `mach_absolute_time()` does not advance; contiguous pages are preallocated during STARTUP.
- **`IOSleep()` never returns on this platform**, so any deadline-based wait hangs; waits must spin and yield instead.
- The IOStorageFamily prelink absolute symbols were missing the board slide \(`-0x1000000`\), so the block-device constructor branched into zero-filled padding \(`UDF #0`\).
- `IOService::registerService()` silently drops a service that has no path to the registry root in the service plane; this port attaches the windows to the platform expert instead.

## Current blocker

The windows register \(`REGPUBLISH ok` in the diagnostics\) but no `IOBlockStorageDriver` claims the device, so no `IOMedia` appears and the media wait expires: `UFS ROOT FAILURE: SystemOS window media not found`.

See `docs/bringup-2026-11-19-session.md` in the repository for the full record, the hypotheses already excluded and the next steps.