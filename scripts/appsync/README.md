# AppSync adapter for UniXNU

The sheng iPadOS 27.0.1 (24A446) adapter applies to all user application bundles,
including unsigned, fakesigned and expired packages. Applications and updates
are installed on device without a build-time list or image rebuild.

It follows [AppSync Unified](https://github.com/akemin-dayo/AppSync/tree/235aca6cddfbdc9fa87fcb5b2aec2df37ed6d65a)'s
separation of installation validation, FrontBoard launch trust and the
LSApplicationWorkspace installer. Upstream authors: Karen/あけみ and Linus Yang.
The Objective-C adaptation is GPL-3.0-or-later. This is an independent UniXNU
port; real device installation and launch remain unverified.

## Install applications

Build and boot the sheng 24A446 image with its original Data seed and firmware
inputs. The board selects `payload.runtime.appsync = true` and `appsync=1`.
There are no per-application build options. Transfer any compatible IPA to the
device, then run:

```sh
/usr/libexec/unixnu-appinst /path/on/device/Example.ipa
```

Other installers using MobileInstallation use the same hooks. The optional
older syntax `unixnu-appinst BUNDLE_ID FILE.ipa` also works. The tool gives the
native installer a private copy so it cannot consume the supplied IPA.
Installation is not started automatically by boot or packaging. Existing apps
with usable signature structures are covered after boot without a general
reinstall. Truly unsigned or structurally damaged code needs the installation
repair path before launch.

## Installation and signature repair

`AppSync.m` hooks `MICodeSigningVerifier` in installd and
MobileInstallationHelperService. It enables native ad-hoc signing, disables
preloaded trust-cache and online authorization requirements, and skips profile
ID validation for every `.app` tree on Data (`/private/var/` or `/var/`). This
includes installation staging, embedded frameworks and extensions. Original
options are restored on success, failure and exceptions.

`Signing.m` first invokes the original verifier. If it rejects a user package,
the adapter locks that bundle, preflights its Mach-O slices, removes obsolete
embedded provisioning profiles, and runs the bundled signer recursively. The
signer preserves existing XML/DER entitlements, regenerates code and resource
signatures, and marks signatures without a CMS identity as ad-hoc. The original
verifier then validates the result and creates native signing information.
Valid packages remain unchanged. Concurrent repairs serialize on the bundle;
a failed signer or second validation remains an installation failure.

The signer is [Procursus ldid](https://github.com/ProcursusTeam/ldid), with the
small `ldid-adhoc.patch` required by this AMFI path. `signer-sources.json` pins
its source and the static OpenSSL/libplist dependencies by commit and archive
SHA-256. `signer.py` builds an arm64 iOS executable with only libSystem and
libc++ dynamic dependencies. Build downloads are cached; on-device signing is
offline. Licenses accompany the runtime; the cache retains ldid objects and
static libraries for relinking. See `LICENSE` and the pinned upstream sources.

Malformed Mach-O commands, encrypted slices and symlinks escaping the bundle
are rejected before repair. There is a 120-second signer deadline. This port
does not decrypt FairPlay content or supply App Store account authorization;
packages still need executable code compatible with the target OS and CPU.

## Launch and kernel trust

FrontBoard's `FBSSignatureValidationService trustStateForApplication:` returns
its trusted state (8) for all user bundles. Every hook checks the private method
ABI before activation. System bundle paths retain native behavior.

The `sheng-appsync-user-trust.patch` calls `appsync_trust_user_code` from
`ubc_cs_blob_add`, after XNU validates the signature structure and computes the
CodeDirectory hash and before AMFI verifies it. The kernel adds that hash using
the engineering trust-cache interface already used for owner boot modules.
New applications, updated executables and nested libraries are handled on demand.
VM page hashes and AMFI callbacks still run. No client can submit an arbitrary
hash through a user-accessible registration API.

Registration deduplicates under the trust runtime lock and retains successful
modules until reboot. The next boot registers an app again on first mapping.
There is a 65536-module memory bound per boot; allocation/load failures are
reported and reject the mapping. Like other trust-cache entries, registration
trusts the same code hash for the rest of that boot, even if its file moves.
`appsync=0` disables both runtime mounts and automatic registration.

## Packaging and verification

`build.py` pins the three original 24A446 executable inputs. It routes their
Foundation dependency through the signed adapter, which re-exports Foundation,
preserving ordinals, code addresses and chained/PAC fixups. Native identifiers
and entitlements are checked after signing. The boot trust bundle includes
these runtime copies and `unixnu-ldid`; user application hashes are not build
inputs. `appsync-service.json` records `scope = "all-user-bundles"`,
`dynamic_user_trust = true`, `signature_repair = true` and the source pins.

From UniXNU on macOS with Xcode and Python 3.13 or later:

```sh
python3.13 scripts/appsync/test.py --signing --os-root /readonly/24A446/OS \
  --os-image /path/to/24A446/OS.dmg
python3.13 scripts/test-runtime-inputs.py
```

The host suite runs production hooks and repair code under ASan/UBSan. It
checks unknown apps/updates, nested bundles, unsigned and multi-architecture
Mach-O files, non-Apple and expired certificate fixtures, resource/profile
repair, entitlement preservation and rejected encrypted/escaping inputs.
Repaired outputs are independently checked with Apple's codesign tool. The
first iOS certificate rejection is modeled on the host; Apple's actual iOS
verifier, dyld and SpringBoard still require a device test.

The exact kernel registration source is extracted from the board patch and
compiled with a mock trust runtime to test concurrent deduplication, updates,
frameworks, disabled behavior and allocation/load failures. Full kernel and
image builds separately check the real XNU declarations and linkage. Runtime
packing tests verify original trust-module and Data preservation and repeat
builds. Device checkpoints are installation, registration, launch, extensions,
updates and persistence across reboot.
