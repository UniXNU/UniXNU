# XnuPrelink

Start with the [adaptation procedure](/porting/platform) for board inputs, source changes, build integration and verification order.

Kernel prelink emitter and ABI tooling.

[Source repository](https://github.com/UniXNU/XnuPrelink).

XnuPrelink binds the built XNU kernel to selected original kexts and writes the prelink plan. The OS profile supplies the kernelcache pin, roots, slide, and ABI settings.

For arm64e fileset kernel collections, `emit_prelink.py` selects the fileset
emitter and generates a function/data map. `--fileset-map FILE` supplies an
existing map with matching input hashes and matcher version. The selected roots
and their dependency closure are retained.
Code comparison accounts for complete compiler-inserted PAC failure checks;
the emitted native code retains them. Both emitter entry points validate the
matching code signature before reusing a map.
`--fileset-reference FILE` supplies an additional kernel with symbols for code
comparison. It transfers unambiguous names from unique code matches and resolves
those names in the actual native kernel. The map records the reference hash.

The sheng iPadOS 27 build runs `build-fileset-release-reference.py --tree . --lto`
before prelinking. Keep LTO enabled for this comparison: the non-LTO reference
loses matches needed by original kexts, including corecrypto's startup call to
`kprintf`. With `--allow-missing`, such a call reaches `unixnu_fileset_unmapped`
at runtime even though packaging succeeds.

The reference builder records its mode, source, SDK, archive, compiler and
version inputs and verifies the output digest before reusing it. Unrecorded
references are rebuilt. Different inputs use separate build directories;
LTO export inspection reads the generated LTO object and non-LTO file list.
After a reference change, regenerate the map, kernel, payload and boot image,
and inspect the unresolved-target report before hardware testing.

The 24A446 fixture preserves 23 import identities recovered from the retained
RELEASE-LTO map and cross-checked against its boot image, plus the observed
corecrypto `kprintf` import. Their original function digests and recovery
provenance are recorded; the current native targets are resolved by symbol.
The fixture also identifies 13 previously missing vnode operation descriptors by
`vdesc_name`, four metaclass pointer slots by their chained targets, and the
`gIODTPHandleKey` and `audio_active` globals by their source consumers. Unbound
vnode descriptors can make APFS registration read a zone field as an operation
index in `vfs_fsadd`; they must resolve to the native descriptors initialized by
VFS, not preserve old collection data addresses.


The emitter places native segments within the collection's code, constant and
data ranges, applies native split-segment records, rebuilds chained fixups and
function starts, and recomputes corecrypto's code HMAC. The collection root uses
the native link address. The ordinary prelink `--slide` value does not apply to
filesets. The native input executable is unchanged.

Native adapters to retained kext functions declare fixed targets as `N_ABS`
`<stub>.original` symbols and use `BTI c; B` stubs. These branches lack linker
split-segment records, so the emitter recomputes them after placement and checks
every destination against retained executable ranges. The report records each
binding in `native_original_branches`. Builders must not pre-subtract a cached
native slide. Absolute data pointers in GOT entries keep their fixed values.

Missing mappings stop emission by default. `--allow-missing` produces an
experimental image and the JSON report lists every unresolved target by kext.
An image that passes structural checks still requires complete mappings and
hardware validation before boot compatibility can be established.

`unixnu kernel --skip-prelink` stages the native executable as `kernel.macho`.
`unixnu prelink --skip-prelink` stages an existing build. This mode does not add
the original kexts and records `native-only` beside the output.

## Integration

The catalog records implementation scope, hardware and OS requirements, board dependencies, revision, build stage, outputs, and runtime identifiers. The selected profile orders build commands by dependency.

```sh
./unixnu build prelink -D ../UniXNU-sheng
```

[Component catalog](/reference/components)

The 24A446 packaging profile additionally checks a regression policy against the
original (unslid) imported targets. New unresolved data or stubbed calls fail
before replacing the last kernel candidate. This caught two lost order-based
matches during a full rebuild: `IOCircularDataQueueCopyLatest` and `get_aiotask`;
the reviewed fixture now identifies both by original digest and native symbol.
